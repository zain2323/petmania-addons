from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist.item'

    extra_discount = fields.Float(string="Discount%")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_get_discount(self):
        if self.product_id:
            order = self.order_id
            pricelist_items = order.pricelist_id.item_ids.filtered(lambda line: line.product_tmpl_id.id == self.product_id.product_tmpl_id.id)
            for pricelist_item in pricelist_items:
                if pricelist_item.extra_discount and self.product_uom_qty == pricelist_item.min_quantity:
                    self.discount = pricelist_item.extra_discount