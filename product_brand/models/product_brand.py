# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _order = "name"

    name = fields.Char("Brand Name", required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        help="Select a partner for this brand if any.",
        ondelete="restrict",
    )
    logo = fields.Binary("Logo File")
    product_ids = fields.One2many(
        "product.template", "product_brand_id", string="Brand Products"
    )
    products_count = fields.Integer(
        string="Number of products", compute="_compute_products_count"
    )

    @api.depends("product_ids")
    def _compute_products_count(self):
        product_model = self.env["product.template"]
        groups = product_model.read_group(
            [("product_brand_id", "in", self.ids)],
            ["product_brand_id"],
            ["product_brand_id"],
            lazy=False,
        )
        data = {group["product_brand_id"][0]: group["__count"] for group in groups}
        for brand in self:
            brand.products_count = data.get(brand.id, 0)
