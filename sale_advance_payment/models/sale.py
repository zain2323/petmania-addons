# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    due_payment = fields.Float(string='Advance Paid', digits='Product Price', compute='_compute_payment', store=True, compute_sudo=True)
    payment_count = fields.Integer(string='Payments', compute='_compute_payment', compute_sudo=True)
    sale_payment_ids = fields.One2many('account.payment', 'sale_id', string="Advanced sale payment", readonly=True)

    def action_view_payment(self):
        pay_records = self.env['account.payment']
        sale_payment_ids = self.mapped('sale_payment_ids')
        invoice_payment_ids = self.env['account.payment'].search([('reconciled_invoice_ids', 'in', self.mapped('invoice_ids').ids), ('id', 'not in', sale_payment_ids.ids)])
        pay_records |= sale_payment_ids + invoice_payment_ids
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', pay_records.ids)],
        }

    @api.depends('sale_payment_ids', 'invoice_ids', 'state', 'invoice_status')
    def _compute_payment(self):
        all_records = self.env['account.payment']
        for order in self:
            sale_payment_ids = order.mapped('sale_payment_ids')
            in_payment_ids = sale_payment_ids.filtered(lambda x: x.payment_type == 'inbound')
            out_payment_ids = sale_payment_ids.filtered(lambda x: x.payment_type == 'outbound')
            invoice_ids = order.mapped('invoice_ids')
            inv_payment_ids = self.env['account.payment'].search([('reconciled_invoice_ids', 'in', invoice_ids.ids), ('id', 'not in', sale_payment_ids.ids), ('state', '=', 'cancelled')])
            all_records |= sale_payment_ids + inv_payment_ids
            if out_payment_ids:
                order.due_payment = 0.0
            else:
                order.due_payment = sum(in_payment_ids.mapped('amount'))
            order.payment_count = len(all_records.ids)
