from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_scm_grading_id = fields.Many2one(comodel_name="scm.grading", string="SCM Grading")

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """,t.product_scm_grading_id"""
        return res

    def _select_additional_fields(self, fields):
        fields["product_scm_grading_id"] = ", t.product_scm_grading_id as product_scm_grading_id"
        return super()._select_additional_fields(fields)
