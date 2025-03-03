from odoo import fields, models, api, _
from odoo.tools import float_compare

class ProductProduct(models.Model):
    _inherit = 'product.product'

    follow_vendor_moq_rule = fields.Boolean('Follow Vendor Minimum Quantity Rule ?', default=False)
    capping_qty = fields.Float("Highest sales qty level", help="""
    Ignore all sales if the sales qty is above the defined highest level in the reordering average sales calculation
    """)
    update_orderpoint = fields.Boolean("Update Order Point?", default=True,
                                               help="By configuring this by True, order points of this product will be "
                                                    "automatically updated.")

    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env['product.supplierinfo']
        sellers = self._prepare_sellers(params)
        if self.env.context.get('force_company'):
            sellers = sellers.filtered(
                lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
        for seller in sellers:
        # Set quantity in UoM of seller
            quantity_uom_seller = quantity #if quantity is not None else 0
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            if quantity is not None and float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            if not res or res.name != seller.name:
                res |= seller
        sort_parameter = self.env.context.get("sory_by", "sequence")
        if sort_parameter == 'price':
            company_id = self.env.context.get("op_company")
            return res.sorted(key=lambda x: x.currency_id._convert(x.price, company_id.currency_id, company_id, date))[:1]
        else:
            return res.sorted(sort_parameter)[:1]


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    reorder_minimum_quantity = fields.Float('Reorder Minimum Quantity', help='Set Minimum Quantity for Reorder Summary')
