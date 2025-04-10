# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _


class CustomerOrderBooker(models.Model):
    _name = "customer.order.booker"
    _description = "Customer Order Booker"
    _rec_name = 'name'

    name = fields.Char(string="Type")

