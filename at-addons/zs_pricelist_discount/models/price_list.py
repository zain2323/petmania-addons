from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist.item'

    extra_discount = fields.Float(string="Discount%")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_get_discount(self):
        if self.product_id:
            order = self.order_id
            pricelist_item = order.pricelist_id.item_ids.filtered(lambda line: line.product_tmpl_id.id == self.product_id.product_tmpl_id.id)
            if pricelist_item and pricelist_item.extra_discount:
                self.discount = pricelist_item.extra_discount