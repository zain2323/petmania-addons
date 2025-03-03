from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    bank_charges_percent = fields.Float(string="Bank Charges %")
    bank_charges_product = fields.Many2one('product.product', string="Bank Charges Product")