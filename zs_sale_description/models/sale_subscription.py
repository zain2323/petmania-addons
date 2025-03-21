from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    order_type = fields.Selection([('delivery', 'Delivery'),
                                   ('pickup', 'Pickup'), ], "Order Type", default='delivery',
                                  help="Order type such as delivery or pickup")


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    order_type = fields.Selection([('delivery', 'Delivery'),
                                   ('pickup', 'Pickup'), ], "Order Type", default='delivery',
                                  help="Order type such as delivery or pickup")

    def _prepare_invoice(self):
        invoice = super(SaleSubscription, self)._prepare_invoice()
        invoice['order_type'] = self.order_type
        return invoice
