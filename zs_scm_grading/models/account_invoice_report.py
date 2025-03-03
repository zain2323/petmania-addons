from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_scm_grading_id = fields.Many2one(comodel_name="scm.grading", string="SCM Grading")

    @api.model
    def _select(self):
        select_str = super()._select()
        select_str += """
            , template.product_scm_grading_id as product_scm_grading_id
            """
        return select_str

    @api.model
    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", template.product_scm_grading_id"
        return group_by_str
