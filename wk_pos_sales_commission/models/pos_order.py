# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    def _compute_is_multiple_invoice_enable(self):
        val = self.env['ir.default'].sudo().get('res.config.settings', 'multiple_invoice')
        self.multiple_invoice = val

    def _get_commission(self):
        for order in self:
            pos_commissions = self.env['pos.commission'].search([('order_id', '=', order.id)])
            order.commission_count = len(pos_commissions)

    is_commission = fields.Boolean(string='Is Commission')
    is_multiple_invoice_enable = fields.Boolean(string='Use Hr Employee Config', compute='_compute_is_multiple_invoice_enable')
    commission_count = fields.Integer(string='Commission Count', compute='_get_commission', readonly=True)

    def action_view_commission(self):
        action = self.env.ref('wk_pos_sales_commission.commission_pos_commission_view').read()[0]
        action['domain'] = [('order_id', '=', self.id)]
        return action

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(order, draft, existing_order)
        commission_id = None
        commission_id = self.get_commission_config(order)        
        commission_vals = self.env['pos.sale.commission'].browse([commission_id])        
        # Check is commission is based on total sale amount or on rules
        auto_confirm = self.env['ir.default'].sudo().get('res.config.settings', 'auto_confirm_at_order_validation')
        if(commission_vals.commission_rule == 'amount'):
            if(commission_id):
                if(order and order.get('data') and order.get('data').get('is_commission')):
                    amount_total = order.get('data').get('amount_total')
                    commission_amount = self.env['pos.sale.commission'].compute_commission_based_on_amount(amount_total, commission_id)
                    product = self.env['product.product'].search([('is_commission_product', '=', True)])

                    partner = order.get('data').get('user_id')
                    employee = order.get('data').get('employee_id')

                    apply_commission = False
                    if(employee):
                        if(self.env['hr.employee'].browse([employee]).is_commission_applicable):
                            apply_commission = True
                    else:
                        if(partner and self.env['res.users'].browse([partner]).is_commission_applicable):
                            apply_commission = True

                    if(apply_commission):
                        self.create_commission(product, commission_amount, partner, employee, order_id, auto_confirm)
        else:
            create_commission = 'single'
            create_commission = self.env['ir.default'].sudo().get('res.config.settings', 'create_commission')
            if(commission_id):
                if(create_commission == 'multiple'):
                    if(order and order.get('data') and order.get('data').get('is_commission')):
                        partner = None
                        total_commission_amount = 0.0 
                        if(order.get('data').get('lines')):
                            for line in order.get('data').get('lines'):
                                product = line[2].get('product_id')
                                qty = line[2].get('qty')
                                price_unit = line[2].get('price_unit')

                                partner = order.get('data').get('user_id')
                                employee = order.get('data').get('employee_id') 

                                apply_commission = False
                                if(employee):
                                    if(self.env['hr.employee'].browse([employee]).is_commission_applicable):
                                        apply_commission = True
                                else:
                                    if(partner and self.env['res.users'].browse([partner]).is_commission_applicable):
                                        apply_commission = True
                                wk_product = self.env['product.product'].search([('id', '=', product)])
                                commission_amount = self.env['pos.sale.commission'].compute_commission(product, price_unit, qty,commission_id)
                                if(apply_commission):
                                    self.create_commission(wk_product, commission_amount, partner, employee, order_id, auto_confirm)
                else:
                    if(order and order.get('data') and order.get('data').get('is_commission')):
                        partner = None
                        val_line = []
                        total_commission_amount = 0.0
                        employee = order.get('data').get('employee_id') 
                        if(order.get('data').get('lines')):
                            for line in order.get('data').get('lines'):
                                product = line[2].get('product_id')
                                qty = line[2].get('qty')
                                price_unit = line[2].get('price_unit')

                                commission_amount = self.env['pos.sale.commission'].compute_commission(product, price_unit, qty,commission_id)
                                val = self.env['res.users'].search([('id', '=', order.get('data').get('user_id'))])
                                
                                partner = order.get('data').get('user_id')
                                
                                apply_commission = False
                                if(employee):
                                    if(self.env['hr.employee'].browse([employee]).is_commission_applicable):                                        
                                        apply_commission = True
                                else:
                                    if(partner and self.env['res.users'].browse([partner]).is_commission_applicable):
                                        apply_commission = True
                                
                                if(apply_commission and commission_amount):
                                    total_commission_amount = total_commission_amount + commission_amount
                                    val_line.append([0,0,{
                                                    'product_id' : product,
                                                    'commission_amount' : commission_amount,
                                                    'user_id': partner,
                                                    'employee_id': employee,
                                                    'order_id': order_id,
                                                    'qty' : qty,
                                                    'price_unit' : price_unit,
                                                }])
                                                
                        vals = {}
                        vals['user_id'] = partner
                        vals['employee_id'] = employee
                        vals['order_id'] = order_id  
                        vals['pos_commission_line_ids'] = val_line
                        vals['commission_amount'] = total_commission_amount
                            
                        if(total_commission_amount and len(val_line)):
                            self.auto_confirm(vals, auto_confirm)
        return order_id

    def get_commission_config(self, order):
        # Res Config Commission Data
        res_config_commission = self.get_res_config_setting_data()

        # Res Config get default commission
        if(res_config_commission.get('sale_commission_id')):
            commission_id = res_config_commission.get('sale_commission_id')

        # Res Config check is pos config true, and get Pos Config Commission data
        if(res_config_commission.get('use_pos_congif_commission')):
            session = self.env['pos.session'].search([('id', '=', order.get('data').get('pos_session_id'))])
            config = self.env['pos.config'].search([('id', '=', session.config_id.id)])
            if(config and config.use_different_commission):
                if(config.sale_commission_id):
                    commission_id = config.sale_commission_id.id
            
        return commission_id

    def create_commission(self, product, commission_amount, partner, employee, order_id, auto_confirm):
        val_line = []
        if(commission_amount):            
            val_line.append([0,0,{
                            'product_id' : product.id,
                            'commission_amount' : commission_amount,
                            'user_id': partner,
                            'employee_id': employee,
                            'order_id': order_id,
                            'qty' : 1,
                            'price_unit' : commission_amount,
                        }])
        vals = {}
        vals['user_id'] = partner
        vals['employee_id'] = employee
        vals['order_id'] = order_id  
        vals['pos_commission_line_ids'] = val_line
        vals['commission_amount'] = commission_amount
        if(commission_amount and len(val_line)):
            self.auto_confirm(vals, auto_confirm)

    def auto_confirm(self, vals, auto_confirm):
        data = self.env['pos.commission'].create([vals])
        if(data and auto_confirm):
            data.state = "confirm"

    @api.model
    def get_res_config_setting_data(self):
        val = {}
        val['use_pos_congif_commission'] = self.env['ir.default'].sudo().get('res.config.settings', 'use_pos_congif_commission')
        val['sale_commission_id'] = self.env['ir.default'].sudo().get('res.config.settings', 'sale_commission_id')
        return val
