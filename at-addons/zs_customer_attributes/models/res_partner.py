# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_attributes = fields.Many2one('customer.attributes', string='Customer Atttributes')