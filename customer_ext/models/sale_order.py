# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_booker_id = fields.Many2one('customer.order.booker', string="Order Booker")
    type_id = fields.Many2one('customer.type', string='Customer Type')

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('partner_id'):
            self.order_booker_id = self.partner_id.order_booker_id
            self.type_id = self.partner_id.type_id
        return res


    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        for rec in res:
            if rec.partner_id:
                rec.order_booker_id = rec.partner_id.order_booker_id
        return res
