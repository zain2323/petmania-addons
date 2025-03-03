# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api


class CreateReordering(models.TransientModel):
    _inherit = 'create.reordering'

    slab_id = fields.Many2one('reordering.slab.qty')

    def create_reorder_rule(self):
        location_type = self.location_selection_strategy
        products = self.product_ids and set(self.product_ids.ids) or {}
        inserted_orderpoints_ids = []
        if location_type == 'specific':
            specific_location_mapping_ids = self.specific_location_mapping_ids
            if not specific_location_mapping_ids:
                raise UserError("Please configure warehouses and its specific locations.")
            for mapping in specific_location_mapping_ids:
                op_ids = self.reordering_rule_exec(products, set([mapping.warehouse_id.id]), location_type,
                                                   specific_location=mapping.specific_location_id.id)
                if op_ids:
                    inserted_orderpoints_ids.extend(op_ids)
        else:
            warehouses = self.warehouse_ids
            if not warehouses:
                allowed_company_ids = self.env.context.get('allowed_company_ids', [])
                if allowed_company_ids:
                    warehouses = self.env['stock.warehouse'].sudo().search([]).filtered(
                        lambda x: x.company_id.id in allowed_company_ids)
                    warehouses = warehouses
            for warehouse in warehouses:
                if location_type == 'lot_stock':
                    specific_location = warehouse.lot_stock_id.id
                else:
                    specific_location = warehouse.wh_input_stock_loc_id.id
                op_ids = self.reordering_rule_exec(products, set([warehouse.id]), location_type,
                                                   specific_location=specific_location)
                if op_ids:
                    inserted_orderpoints_ids.extend(op_ids)

        if inserted_orderpoints_ids:
            # orderpoints = self.env['stock.warehouse.orderpoint']
            orderpoints = self.env['stock.warehouse.orderpoint'].browse(inserted_orderpoints_ids)
            if orderpoints and not self.period_ids:
                orderpoints.update_product_purchase_history()
                orderpoints.update_product_sales_history()
                orderpoints.update_product_iwt_history()
                self._cr.commit()

            for record in orderpoints:
                # orderpoint = record#self.env['stock.warehouse.orderpoint'].browse(record)
                vals = {'consider_current_period_sales': self.consider_current_period_sales,
                        'add_purchase_in_lead_calc': self.add_purchase_in_lead_calc,
                        'add_iwt_in_lead_calc': self.add_iwt_in_lead_calc,
                        'buffer_days': self.buffer_days}

                if self.average_sale_calculation_base:
                    vals.update({'average_sale_calculation_base': self.average_sale_calculation_base})
                if self.document_creation_option:
                    vals.update({'document_creation_option': self.document_creation_option})
                if self.vendor_selection_strategy:
                    vals.update({'vendor_selection_strategy': self.vendor_selection_strategy})
                if self.vendor_selection_strategy == 'specific_vendor' and self.partner_id:
                    vals.update({'partner_id': self.partner_id})
                if self.purchase_lead_calc_base_on == 'static_lead_time':
                    vals.update({'max_lead_time': self.static_maximum_lead_time,
                                 'avg_lead_time': self.static_average_lead_time})
                record.with_context(do_not_checked_rule=True).write(vals)

                record.with_context(already_calculated_history=True, do_not_checked_rule=True).recalculate_data()
                # orderpoints += orderpoint
            if orderpoints:
                self._cr.commit()
                orderpoints.update_order_point_data()
                if self.slab_id:
                    for i in orderpoints:
                        i.update({
                            'reordering_slab': self.slab_id.id
                        })
                        i.update_order_point_data()
                else:
                    for i in orderpoints:
                        if not i.product_min_qty and not i.product_max_qty:
                            min_max = self.env['product.product'].search([('id','=',i.product_id.id)],limit=1)
                            i.update({
                                'product_min_qty' : min_max.min,
                                'product_max_qty' : min_max.max,
                            })
            return self.action_orderpoint(orderpoints.ids)
        return True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    min = fields.Integer('Min')
    max = fields.Integer('Max')
