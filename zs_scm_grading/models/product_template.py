from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_scm_grading_id = fields.Many2one(
        "scm.grading", string="SCM Grading",
    )
