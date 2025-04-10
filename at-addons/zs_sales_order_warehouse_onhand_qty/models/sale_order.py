from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_warehouse_qty(self):
        for rec in self:
            rec.onhand_qty = 0
            warehouse = rec.order_id.warehouse_id
            product = rec.product_id.id
            lot_stock_id = warehouse.lot_stock_id.id
            stock_quant = self.env['stock.quant'].search([('location_id', '=', lot_stock_id), ('product_id', '=', product), ('on_hand', '=', True)])
            for quant in stock_quant:
                rec.onhand_qty = quant.quantity

    onhand_qty = fields.Integer(string="Warehouse QTY", compute="get_warehouse_qty", default=0)
