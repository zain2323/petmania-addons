from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import UserError
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        if not self._context.get('custom_order_point_function', False):
            return super(StockRule, self)._run_buy(procurements)
        procurements_by_po_domain = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            domain = [('product_id', '=', procurement.product_id.id),
                      ('location_id', '=', procurement.location_id.id), ('trigger', '=', 'auto')]
            order_point = self.env['stock.warehouse.orderpoint'].search(domain, limit=1)
            if not order_point:
                return super(StockRule, self)._run_buy(procurements)
            partner = supplier = False
            sory_by = "sequence"
            lead_days = 0
            if self._context.get('custom_reordering_category_id', False):
                vendor_name = order_point.product_id.product_vendor_name_id.name
                if not vendor_name:
                    vendor_name = "Undefined vendor"
                partner = self.env['res.partner'].search([('name', '=', vendor_name)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].sudo().create({
                        'name': vendor_name,
                        'company_type': 'company',
                        'supplier_rank': 1
                    })
                supplier = self.find_supplier_info(procurement.product_id, partner)
                lead_days = supplier and supplier.delay or 0
                lead_days_date = fields.Datetime.today() + relativedelta(days=lead_days)
                procurement.values.update({'date_planned': lead_days_date, 'date_deadline': lead_days_date})
                procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
                schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))
            else:
                if order_point.vendor_selection_strategy == "specific_vendor" and order_point.partner_id:
                    partner = order_point.partner_id
                    supplier = self.find_supplier_info(procurement.product_id, partner)
                    lead_days = supplier and supplier.delay or 0
                elif order_point.vendor_selection_strategy == "quickest":
                    sory_by = "delay"
                    lead_days, dummy = rule._get_lead_days(procurement.product_id.with_context(sory_by=sory_by))
                elif order_point.vendor_selection_strategy == "cheapest":
                    sory_by = "price"
                    lead_days, dummy = rule._get_lead_days(procurement.product_id.with_context(sory_by=sory_by,
                                                                                               op_company=procurement.company_id))
                if order_point.vendor_selection_strategy in ['quickest', 'cheapest'] or (
                        order_point.vendor_selection_strategy == 'specific_vendor' and supplier):
                    lead_days_date = fields.Datetime.today() + relativedelta(days=lead_days)
                    procurement.values.update({'date_planned': lead_days_date,
                                               'date_deadline': lead_days_date})
                procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
                schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))
                if not supplier:
                    supplier = procurement.product_id.with_context(
                        {'sory_by': sory_by, 'op_company': procurement.company_id})._select_seller(
                        quantity=procurement.product_qty,
                        date=schedule_date.date(),
                        uom_id=procurement.product_uom)
                    partner = supplier.name

                if not partner:
                    msg = _(
                        'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                              procurement.product_id.display_name)
                    # raise UserError(msg)
                    errors.append((procurement, msg))

            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
            schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))

            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            # procurement.values['propagate_date'] = rule.propagate_date
            # procurement.values['propagate_date_minimum_delta'] = rule.propagate_date_minimum_delta
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            domain += (('scm_grading_id', '=', order_point.scm_grading_id.id),)
            domain += (('is_suspended', '=', False),)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)
        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            if not po:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
                vals.update({'date_order': fields.datetime.today()})
                vals.update({'scm_grading_id': order_point.scm_grading_id.id})
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.

                po = self.env['purchase.order'].with_company(company_id.id).sudo().create(vals)
            else:
                # If a purchase order is found, adapt its `origin` field.
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    if missing_origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                else:
                    po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(
                po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(
                    'product_id'), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                                                            procurement.product_qty, procurement.product_uom,
                                                            company_id,
                                                            procurement.values, po_line)
                    po_line.write(vals)
                else:
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
            self.env['purchase.order.line'].sudo().create(po_line_values)

    def find_supplier_info(self, product, partner):
        supplier = self.env['product.supplierinfo'].search(
            [('name', '=', partner.id), ('product_tmpl_id', '=', product.product_tmpl_id.id),
             ('product_id', '=', product.id), ('company_id', '=', self.env.company.id)], limit=1)
        if not supplier:
            supplier = self.env['product.supplierinfo'].search(
                [('name', '=', partner.id), ('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)
        if not supplier and self._context.get('custom_reordering_category_id', False):
            supplier = self.env['product.supplierinfo'].create(
                {'name': partner.id, 'product_id': product.id, 'price': product.list_price})
        return supplier


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain()
        if self._context.get('custom_reordering_category_id', False):
            domain += [('scm_grading_id', '=', self._context.get('custom_reordering_category_id'))]
        return domain
