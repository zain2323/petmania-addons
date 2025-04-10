from odoo import api, fields, models, exceptions


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Adding the functionality to automatically confirm invoices"""
        invoices = super(SaleOrder, self)._create_invoices(grouped, final, date)
        for invoice in invoices:
            invoice.action_post()
        return invoices

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleOrder, self)._create_invoice(order, so_line, amount)
        invoice.action_post()
        return invoice