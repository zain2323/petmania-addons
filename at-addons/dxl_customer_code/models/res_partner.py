# -*- coding: utf-8 -*-
from odoo import models,fields,api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    client_code_ids = fields.Many2many("res.partner.code",string="Client Code",compute = 'get_client_code_by_partner')

    def get_client_code_by_partner(self):
        partner_code_obj = self.env['res.partner.code'].search([('name', 'in', self.ids)])
        vals_partner_code = []
        for rec in partner_code_obj:
            vals_partner_code.append(rec.id)
        self.client_code_ids = vals_partner_code
