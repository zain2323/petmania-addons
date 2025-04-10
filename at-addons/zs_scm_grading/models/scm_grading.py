from odoo import api, fields, models


class ScmGrading(models.Model):
    _name = "scm.grading"
    _order = "name"

    name = fields.Char("SCM Grading", required=True)
    is_trial = fields.Boolean("Is Trial")
    description = fields.Text()
    product_ids = fields.One2many(
        "product.template", "product_scm_grading_id", string="SCM Grading Products"
    )
    products_count = fields.Integer(
        string="Number of products", compute="_compute_products_count"
    )

    @api.depends("product_ids")
    def _compute_products_count(self):
        product_model = self.env["product.template"]
        groups = product_model.read_group(
            [("product_scm_grading_id", "in", self.ids)],
            ["product_scm_grading_id"],
            ["product_scm_grading_id"],
            lazy=False,
        )
        data = {group["product_scm_grading_id"][0]: group["__count"] for group in groups}
        for scm_grading in self:
            scm_grading.products_count = data.get(scm_grading.id, 0)
