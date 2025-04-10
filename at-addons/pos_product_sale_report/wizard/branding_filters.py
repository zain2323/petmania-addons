# -*- coding: utf-8 -*-
from odoo import fields, models, _

class BrandingFilters(models.TransientModel):
    _name = "branding.filters"
    _description = "Branding Filters"

    date_from = fields.Date()
    date_to = fields.Date()
    product_brand_ids = fields.Many2many(
        string="Brands",
        comodel_name='product.brand',
        relation='rel_brand_ref_product_ref',
        column1='brand_ref',
        column2='product_ref',
    )

    def action_generate_report(self):
        action = self.env.ref('pos_product_sale_report.action_pos_sale_report')
        action.sudo().write({'name': "POS Sale Report From " + str(self.date_from) + "To " + str(self.date_to)})
        return action.report_action(self, data={'form': self.read([])[0]})
