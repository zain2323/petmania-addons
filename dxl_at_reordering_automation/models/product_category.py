# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    show_in_report = fields.Boolean('Show in Report')
