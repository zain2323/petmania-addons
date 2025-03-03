# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    type_id = fields.Many2one('customer.type', string='Customer Type')
    order_booker_id = fields.Many2one('customer.order.booker', string="Order Booker")
    is_customer = fields.Boolean(compute='compute_is_customer')

    @api.depends('customer_rank')
    def compute_is_customer(self):
        for rec in self:
            rec.is_customer = False
            if rec.customer_rank > 0:
                rec.is_customer = True