# -*- coding: utf-8 -*-
from odoo import fields,models,api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    client_code = fields.Char("ISM", compute='_compute_client_code')

    @api.depends('product_id','move_id.partner_id')
    def _compute_client_code(self):
        for line in self:
            client_code = ''
            if line.product_id and line.move_id.partner_id:
                clnt_code_obj = self.env['res.partner.code'].search([('partner_id','=', line.move_id.partner_id.id),('product_id','=',line.product_id.id)], limit=1)
                if clnt_code_obj:
                    client_code = clnt_code_obj.client_code
            line.client_code = client_code
