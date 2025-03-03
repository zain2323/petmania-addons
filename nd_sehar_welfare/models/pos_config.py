from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sehar_welfare_product_lines = fields.One2many(
        'sehar.welfare.product.line',
        'pos_config_id',
        string="Sehar Welfare Products"
    )

    sehar_welfare_password_1 = fields.Char(string="Sehar Welfare Password 1")
    sehar_welfare_password_2 = fields.Char(string="Sehar Welfare Password 2")

class SeharWelfareProductLine(models.Model):
    _name = 'sehar.welfare.product.line'
    _description = 'Sehar Welfare Product Line'

    product_id = fields.Many2one('product.product', string="Product")
    pos_config_id = fields.Many2one('pos.config', string="Pos Config", ondelete='cascade')
