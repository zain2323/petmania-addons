from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist.item'

    extra_fee_percent = fields.Float(string="Extra Fee %")

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        computed_price = super()._compute_price(price, price_uom, product, quantity, partner)
        if self.extra_fee_percent:
           computed_price += price * (self.extra_fee_percent/100)
        return computed_price