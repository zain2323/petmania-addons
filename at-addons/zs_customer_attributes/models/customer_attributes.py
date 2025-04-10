# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class CustomerAttributes(models.Model):
    _name = "customer.attributes"
    _description = "Customer Attributes"
    _rec_name = 'name'

    name = fields.Char(string="Customer Attributes")