from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = super(ProductProduct, self).create(vals)
            product.company_id = False
        return product
