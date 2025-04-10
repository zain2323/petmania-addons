# -*- coding: utf-8 -*-
from odoo import fields,models,api


class StockMove(models.Model):
    _inherit = 'stock.move'

    client_code = fields.Char("ISM", compute='_compute_client_code')

    @api.depends('product_id','picking_id.partner_id')
    def _compute_client_code(self):
        for move in self:
            client_code = ''
            if move.partner_id and move.product_id:
                clnt_code_obj = self.env['res.partner.code'].search([('partner_id', '=', move.picking_id.partner_id.id), ('product_id', '=', move.product_id.id)], limit=1)
                client_code = clnt_code_obj and clnt_code_obj.client_code or ''
            move.client_code = client_code
