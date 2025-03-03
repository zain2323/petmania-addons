# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    po_line_state = fields.Selection([
        ('done', ''),
        ('blocked', '')], string='Status',
        compute='compute_po_line_state')


    @api.depends('product_id.qty_available')
    def compute_po_line_state(self):
        for rec in self:
            if rec.product_id.product_tmpl_id.qty_available > 0:
                rec.po_line_state = 'done'
            else:
                rec.po_line_state = 'blocked'
