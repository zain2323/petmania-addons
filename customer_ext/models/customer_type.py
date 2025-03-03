# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class CustomerType(models.Model):
    _name = "customer.type"
    _description = "Customer Type"
    _rec_name = 'name'

    name = fields.Char(string="Type")
