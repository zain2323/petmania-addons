# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo import api, fields, models, _
from datetime import datetime
from dateutil import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('approval', 'To be Approved'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    visible_approval = fields.Boolean(compute='_compute_visible_approval')

    def _compute_visible_approval(self):
        for order in self:
            if order.state == 'approval' and self.env.user.has_group('dxl_customer_credit_limit.group_credit_limit_approval'):
                order.visible_approval = True
            else:
                order.visible_approval = False

    def _get_pending_payment(self):
        payment_term_lines = self.env['account.payment.term.line'].sudo().search([('payment_id', '=', self.partner_id.property_payment_term_id.id)])
        days = sum(payment_term_lines.mapped('days'))
        term_date = fields.Date.context_today(self) - relativedelta.relativedelta(days=days)
        overdue_invoices = self.env["account.move"].sudo().search([
            ('partner_id','=', self.partner_id.id),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('partner_id.property_payment_term_id', '=', self.partner_id.property_payment_term_id.id),
            ('invoice_date', '<=', term_date),
        ])
        overdue_amount = sum(overdue_invoices.mapped('amount_residual'))
        due_invoices = self.env["account.move"].sudo().search([
            ('partner_id','=', self.partner_id.id),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('partner_id.property_payment_term_id', '=', self.partner_id.property_payment_term_id.id),
            ('invoice_date', '>=', term_date),
        ])
        due_amount = sum(due_invoices.mapped('amount_residual'))
        # past_orders = self.env["sale.order"].sudo().search([
        #     ('partner_id','=', self.partner_id.id),
        #     ('state', 'in', ('sale', 'done')),
        #     ('invoice_status', 'in', ('no', 'to invoice')),
        #     ('payment_term_id', '=', self.partner_id.property_payment_term_id.id),
        #     ('date_order', '<', term_date),
        # ])
        return overdue_amount, due_amount

    def action_approve(self):
        if not self.env.user.has_group('dxl_customer_credit_limit.group_credit_limit_approval'):
            raise UserError(_('You do not have rights to confirm your own sales order!'))
        else:
            self.action_confirm()

    def action_confirm(self):
        restrict_sale_orders = self.env['sale.order'].sudo()
        approver = self.env.user.has_group('dxl_customer_credit_limit.group_credit_limit_approval')
        for so in self:
            overdue_amount, due_amount = so._get_pending_payment()
            if so.state == 'draft' and so.partner_id.credit_limit > 0 and (((due_amount + so.amount_total) > so.partner_id.credit_limit) or overdue_amount > 0):
                restrict_sale_orders |= so
        restrict_sale_orders.write({'state': 'approval'})
        return super(SaleOrder, self.filtered(lambda x: x.id not in restrict_sale_orders.ids)).action_confirm()
