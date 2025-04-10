# #-*- coding:utf-8 -*-


from datetime import date
from odoo import api, models, fields


class LandedCostReport(models.TransientModel):
    _name = "landed.cost.report"

    date_from = fields.Date(string="From ", default=date.today())
    date_to = fields.Date(string="To", default=date.today())
    partner_id = fields.Many2one('res.partner',string="Vendor")
    product_id = fields.Many2one('product.product')
    product_categ_id = fields.Many2one('product.category')
    product_brand_id = fields.Many2one('product.brand')
    purchase_order_id = fields.Many2one('purchase.order')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    def print_xlsx_report(self):
        datas = {
            'wizard_data': self.read()
        }
        return self.env.ref('purchase_landed_report.landed_cost_report').report_action(self, data=datas)
