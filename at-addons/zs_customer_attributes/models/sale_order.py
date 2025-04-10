# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_attributes = fields.Many2one('customer.type', string='Customer Type')

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('partner_id'):
            self.customer_attributes = self.partner_id.customer_attributes
        return res


    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        for rec in res:
            if rec.partner_id:
                rec.customer_attributes = rec.partner_id.customer_attributes
        return res
