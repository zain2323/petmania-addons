from collections import defaultdict

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter

import logging

_logger = logging.getLogger(__name__)


class InventoryOptimisationData(models.TransientModel):
    _name = 'inventory.optimisation.data'
    _description = 'Inventory Optimisation Data'

    wizard_id = fields.Many2one('inventory.optimisation.report.wizard', string='Wizard', required=True)
    product_id = fields.Many2one('product.product', string='Product Id')
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    barcode = fields.Char(string='Barcode')
    min_qty = fields.Integer(string='Min QTY')
    max_qty = fields.Integer(string='Max QTY')
    qty_available = fields.Integer(string='System Count')
    optimisation_qty = fields.Integer(string='Optimisation QTY')
    status = fields.Char(string='Status')

    def _optimize_quantities(self):
        po = {}
        for record in self:
            vendor = record.product_id.product_vendor_name_id
            vendor_name = vendor.name if vendor else "Undefined"
            partner = self.env['res.partner'].search([('name', '=', vendor_name)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': vendor_name,
                    'company_type': 'company',
                    'supplier_rank': 1
                })
            if record.optimisation_qty < 0:
                scm_grading_id = record.product_id.product_scm_grading_id

                # Group by Vendor & SCM Grading ID
                if partner.id not in po:
                    po[partner.id] = {}

                if scm_grading_id not in po[partner.id]:
                    po[partner.id][scm_grading_id] = {
                        'partner_id': partner.id,
                        'order_line': []
                    }

                po[partner.id][scm_grading_id]['order_line'].append((0, 0, {
                    'name': record.product_id.name,
                    'product_id': record.product_id.id,
                    'product_qty': abs(record.optimisation_qty),
                    'product_uom': record.product_id.uom_po_id.id,
                    'price_unit': record.product_id.standard_price,
                    'scm_grading_id': scm_grading_id.id,
                }))

            if record.optimisation_qty > 0:
                source_loc = self.env['stock.location'].search([('usage', '=', 'internal'), ('company_id', '=', self.env.company.id)]).id,
                vendor_loc = self.env['stock.location'].search([('usage', '=', 'supplier')]).id
                picking = self.env['stock.picking'].create({
                    'partner_id': partner.id,
                    'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Internal Transfers'), ('company_id', '=', self.env.company.id)]).id,
                    'location_id': source_loc,
                    'location_dest_id': vendor_loc,
                })
                self.env['stock.move'].create({
                    'name': record.product_id.name,
                    'location_id': source_loc,
                    'location_dest_id': vendor_loc,
                    'picking_id': picking.id,
                    'product_id': record.product_id.id,
                    'product_uom': record.product_id.uom_id.id,
                    'product_uom_qty': abs(record.optimisation_qty),
                })
        # creating rfqs
        for partner_id in po:
            for scm_grading_id in po[partner_id]:
                self.env['purchase.order'].create(po[partner_id][scm_grading_id])


class InventoryOptimisationReportWizard(models.TransientModel):
    _name = 'inventory.optimisation.report.wizard'

    file_data = fields.Binary('File Data')
    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')

    def action_view_pivot(self):
        self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Optimisation Report',
            'res_model': 'inventory.optimisation.data',
            'view_mode': 'tree',
            'target': 'current',
            'context': {'search_default_wizard_id': self.id},
        }

    def _get_data_for_products(self):
        domain = []

        if self.franchise_division_ids:
            domain.append(('company_type', 'in', self.franchise_division_ids.ids))

        if self.product_division_ids:
            domain.append(('product_division_id', 'in', self.product_division_ids.ids))

        if self.product_category_ids:
            domain.append(('categ_id', 'in', self.product_category_ids.ids))

        if self.product_brand_ids:
            domain.append(('product_brand_id', 'in', self.product_brand_ids.ids))

        if self.product_ids:
            domain.append(('id', 'in', self.product_ids.ids))

        products = self.env['product.product'].search(domain)
        products_dict = []
        for product in products:
            reordering_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            qty_available = product.qty_available
            if reordering_rule:
                min_qty = reordering_rule.product_min_qty
                max_qty = reordering_rule.product_max_qty
                optimisation_qty = 0
                status = "ideal"
                if product.qty_available < min_qty:
                    optimisation_qty = qty_available - min_qty
                    status = "deficient"
                if product.qty_available > max_qty:
                    optimisation_qty = qty_available - max_qty
                    status = "surplus"
            else:
                min_qty = 0
                max_qty = 0
                optimisation_qty = 0
                status = "N/A"

            products_dict.append({
                'product_id': product.id,
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'barcode': product.barcode,
                'min_qty': min_qty,
                'max_qty': max_qty,
                'qty_available': qty_available,
                'optimisation_qty': optimisation_qty,
                'status': status,
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        pivot_model = self.env['inventory.optimisation.data']
        pivot_model.search([]).unlink()
        for product_data in products_data:
            pivot_model.create({
                'wizard_id': self.id,
                'product_id': product_data['product_id'],
                'product_name': product_data['product_name'],
                'franchise_name': product_data['franchise_name'],
                'division_name': product_data['division_name'],
                'category_name': product_data['category_name'],
                'brand_name': product_data['brand_name'],
                'barcode': product_data['barcode'],
                'min_qty': product_data['min_qty'],
                'max_qty': product_data['max_qty'],
                'qty_available': product_data['qty_available'],
                'optimisation_qty': product_data['optimisation_qty'],
                'status': product_data['status'],
            })
