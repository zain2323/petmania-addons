from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductInherit(models.Model):
    _inherit = 'product.product'
    use_secondary_name = fields.Boolean(string="Use Secondary Name?", default=False)
    secondary_name = fields.Char(string="Secondary Name")

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    use_secondary_name = fields.Boolean(string="Use Secondary Name?", default=False)
    secondary_name = fields.Char(string="Secondary Name")