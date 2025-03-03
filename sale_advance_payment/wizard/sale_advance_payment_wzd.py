# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleAdvancePayment(models.TransientModel):
    _name = "sale.advance.payment"

    journal_id = fields.Many2one('account.journal', 'Payment Method', required=True)
    amount_to_pay = fields.Monetary(string='Amount', required=True, default=0.0)
    amount_total = fields.Float('Paid Amount', readonly=True)
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)

    def get_paid_amount(self, sale_id):
      amount_to_pay = 0.0
      payments = self.env['account.payment'].search([('sale_id', '=', sale_id.id), ('state', '!=', 'cancelled')])
      if payments:
        amount_to_pay = sum(payments.mapped('amount'))
      return sale_id.amount_total - amount_to_pay

    @api.model
    def default_get(self, fields):
        total_amount = 0.0
        res = super(SaleAdvancePayment, self).default_get(fields)
        sale_id = self.env.context.get('active_id', False)
        if sale_id:
          sale = self.env['sale.order'].browse(sale_id)
          total_amount = self.get_paid_amount(sale)
          res.update({'amount_total': total_amount, 'currency_id': sale.pricelist_id.currency_id.id})
        return res

    @api.constrains('amount_to_pay')
    def _check_valid_payment(self):
      if self.amount_to_pay < 1:
          raise UserError(_("Amount can't be negative or zero !"))
      sale_id = self.env.context.get('active_id', False)
      if sale_id:
        sale = self.env['sale.order'].browse(sale_id)
        if sale and self.amount_to_pay > self.amount_total:
          raise UserError(_("Paid amount must be less than or equal to sale total !"))

    def make_advance_payment(self):
        sale_id = self.env.context.get('active_id', False)
        if sale_id:
            sale = self.env['sale.order'].browse(sale_id)
            exchange_rate = self.env['res.currency']._get_conversion_rate(sale.company_id.currency_id, sale.currency_id, sale.company_id, sale.date_order)
            currency_amount = self.amount_to_pay * (1.0 / exchange_rate)
            payment_dict = {   'payment_type': 'inbound',
                               'partner_id': sale.partner_id and sale.partner_id.id,
                               'partner_type': 'customer',
                               'journal_id': self.journal_id and self.journal_id.id,
                               'company_id': sale.company_id and sale.company_id.id,
                               'currency_id':sale.pricelist_id.currency_id.id,
                               'date': sale.date_order,
                               'amount': currency_amount,
                               'sale_id': sale.id,
                               'name': _("Payment") + " - " + sale.name,
                               'ref': sale.name,
                               'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id
                          }
            payment = self.env['account.payment'].create(payment_dict)
            payment.sudo().action_post()
        return {'type': 'ir.actions.act_window_close'}
