from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    parent_warehouse = fields.Many2one('stock.warehouse', string='Parent Warehouse')