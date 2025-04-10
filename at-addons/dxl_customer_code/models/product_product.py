# -*- coding: utf-8 -*-
from odoo import models,fields,api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    client_code_ids = fields.Many2many("res.partner.code",string="Client Code")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    client_code_ids = fields.Many2many("res.partner.code",string="Client Code",)
