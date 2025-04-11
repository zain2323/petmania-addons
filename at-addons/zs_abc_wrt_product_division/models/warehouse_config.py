from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WarehouseConfig(models.Model):
    _name = 'warehouse.config'

    name = fields.Char(string="Name")
    bond_warehouse = fields.Many2one('stock.warehouse', string="Bond Warehouse")
    company_warehouse = fields.Many2one('stock.warehouse', string="Company Warehouse")
    bond_warehouse_stock_limit = fields.Float(string="Bond Warehouse Stock Limit(%)")
    company_warehouse_stock_limit = fields.Float(string="Bond Warehouse Stock Limit(%)")

    @api.model
    def create(self, vals):
        if self.search_count([]) >= 1:
            raise UserError(_('Only one configuration record is allowed.'))
        return super(WarehouseConfig, self).create(vals)
