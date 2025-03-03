from odoo import api, fields, models, exceptions


class ResCompany(models.Model):
    _inherit = "res.company"
    avg_target_per_day_sale_store = fields.Float(string="Average Target per Day Sale Store")
    avg_target_per_day_sale_clinic = fields.Float(string="Average Target per Day Sale Clinic")
    include_in_sales_report = fields.Boolean(string="Include in Sales Analysis Report?")
    clinic_company_name = fields.Char(string="Clinic Company Name")
