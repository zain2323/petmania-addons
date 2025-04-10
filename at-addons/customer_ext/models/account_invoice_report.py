# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    order_booker_id = fields.Many2one('customer.order.booker', string="Sponsor Captain")
    backup_captain = fields.Many2one('customer.order.booker', string="Backup Captain")
    type_id = fields.Many2one('customer.type', string='Customer Type')
    
class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    order_booker_id = fields.Many2one('customer.order.booker', string="Sponsor Captain", readonly=True)
    backup_captain = fields.Many2one('customer.order.booker', string="Backup Captain", readonly=True)
    type_id = fields.Many2one('customer.type', string='Customer Type', readonly=True)
    
    _depends = {
        'account.move': ['partner_id', 'type_id', 'order_booker_id'],
        'res.partner': ['type_id', 'order_booker_id'],
    }

    def _select(self):
        return super()._select() + ", contact_partner.type_id as type_id, contact_partner.order_booker_id as order_booker_id, contact_partner.backup_captain as backup_captain, move.date"


    # def _from(self):
    #     return super()._from() + " LEFT JOIN res_partner contact_partner ON contact_partner.id = move.partner_id"
