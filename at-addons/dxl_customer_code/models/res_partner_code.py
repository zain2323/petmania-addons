# -*- coding: utf-8 -*-
from odoo import models,fields,api


class ResPartnerCode(models.Model):
    _name = 'res.partner.code'
    _description = 'res.partner.code'
    _rec_name = 'partner_id'
    
    partner_id = fields.Many2one("res.partner","Customer",required=True)
    product_id = fields.Many2one("product.product","Product",required=True)
    client_code = fields.Char("Client Code")
