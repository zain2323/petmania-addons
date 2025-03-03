# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        if not self.user_has_groups('restricts_security.group_restrict_product_creation'):
            raise UserError("Sorry You Are Not Allowed To Create New Products.")
        return super(ProductTemplate, self).create(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        if not self.user_has_groups('restricts_security.group_restrict_product_creation'):
            raise UserError("Sorry You Are Not Allowed To Create New Products.")
        return super(ProductProduct, self).create(vals)
