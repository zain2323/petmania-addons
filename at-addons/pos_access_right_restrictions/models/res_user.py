from odoo import fields, models, api
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = "res.users"

    show_product_info_button = fields.Boolean(
        string="Show Info Button In POS")
    show_orders_menu_button = fields.Boolean(
        string="Show Orders Menu In POS")
    show_edit_onhand_qty = fields.Boolean(
        string="Edit On Hand Quantity In POS")
    show_product_refund_button = fields.Boolean(
        string="Show Refund In POS")

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    def _apply_inventory(self):
        if not self.env.user.show_edit_onhand_qty:
            raise UserError("You do not have sufficient privileges to change stock quantities.")
        super(StockQuant, self)._apply_inventory()