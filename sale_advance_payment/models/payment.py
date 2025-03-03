# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.account.wizard.pos_box import CashBox
from odoo.tools.misc import format_date


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_id = fields.Many2one('sale.order', "Sale Order",)


class AccountMove(models.Model):
    _inherit = 'account.move'

    advance_payment = fields.Float(string='Advance Paid', digits='Product Price', compute='_compute_payment', store=True)

    @api.depends('amount_total', 'amount_residual', 'invoice_line_ids.sale_line_ids')
    def _compute_payment(self):
        all_records = self.env['account.payment']
        for invoice in self:
            sale_payment_ids = invoice.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').mapped('sale_payment_ids')
            inbound_payment_ids = sale_payment_ids.filtered(lambda x: x.payment_type == 'inbound')
            inv_payment_ids = self.env['account.payment'].search([('reconciled_invoice_ids', 'in', invoice.ids), ('id', 'not in', sale_payment_ids.ids)])
            all_records |= inbound_payment_ids
            invoice.advance_payment = sum(all_records.mapped('amount'))
