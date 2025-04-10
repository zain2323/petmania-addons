# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    customer_attributes = fields.Many2one('customer.attributes', string='Customer Attributes')
    
class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    customer_attributes = fields.Many2one('customer.attributes', string='Customer Attributes', readonly=True)
    
    _depends = {
        'account.move': ['partner_id'],
    }

    def _select(self):
        return super()._select() + ", move.customer_attributes as customer_attributes"