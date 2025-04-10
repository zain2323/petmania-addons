# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    total = fields.Float(string="Total")

    def _select(self):
        return super()._select() + ", -line.balance * (line.price_total / NULLIF(line.price_subtotal, 0.0)) AS total"

    def _group_by(self):
        return super()._group_by() + ", -line.balance * (line.price_total / NULLIF(line.price_subtotal, 0.0)) AS total"
