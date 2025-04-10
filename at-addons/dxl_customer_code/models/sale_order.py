# -*- coding: utf-8 -*-
from odoo import models,fields,api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    client_code = fields.Char(string="ISM", compute='_compute_client_code')

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_client_code(self):
        for line in self:
            client_code = ''
            if line.product_id and line.order_id.partner_id:
                partner_code = self.env['res.partner.code'].search([('partner_id', '=', line.order_id.partner_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                client_code = partner_code.client_code
            line.client_code = client_code
