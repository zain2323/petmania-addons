# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, exceptions, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ReorderingReportWizard(models.TransientModel):
    _name = "reordering.report.wizard"
    _description = "Reordering Report Wizard"

    warehouse_id = fields.Many2one('stock.warehouse', required=True, string="Warehouse")
    brand_id = fields.Many2one('product.brand', string="Brand")
    category_ids = fields.Many2many('product.category', 'product_category_rel', string="Category")
    sub_category_ids = fields.Many2many('product.category', 'product_sub_category_rel', string="Sub Category")
    sales_data = fields.Integer(string="Sales Data (in Days)")
    req_storage = fields.Integer(string="Req Storage (in Days)")

    def action_generate_report(self):
        product_domain = []
        if self.brand_id:
            product_domain.append(('product_brand_id', '=', self.brand_id.id))
        if self.category_ids and not self.sub_category_ids:
            product_domain.append(('categ_id', 'child_of', self.category_ids.ids))
        elif self.sub_category_ids:
            product_domain.append(('categ_id', 'in', self.sub_category_ids.ids))

        product_ids = self.env['product.product'].search(product_domain)
        exist_ids = self.env['reordering.report.line'].search([('product_id', 'in', product_ids.ids), ('date', '=', fields.Date.today())]).mapped('product_id')
        tobe_created = product_ids
        sale_back_date = fields.Date.today() - relativedelta(days=self.sales_data)
        if tobe_created:
            for product in tobe_created:
                # sale_moves = self.env['stock.move'].search([('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'customer'), ('product_id', '=', product.id), ('date', '>=', sale_back_date), ('state', '=', 'done')])
                # avg_sales = sum(sale_moves.mapped('product_uom_qty')) / self.sales_data if self.sales_data > 0 else 0
                # req_storage_level = avg_sales * self.req_storage
                self.env['reordering.report.line'].create({
                    'product_id': product.id,
                    'category_id': product.categ_id.parent_id.id,
                    'sub_category_id': product.categ_id.id,
                    'sales_data': self.sales_data,
                    'req_storage': self.req_storage,
                    # 'avg_sales': avg_sales,
                    # 'req_storage_level': req_storage_level,
                    'warehouse_id': self.warehouse_id.id,
                    'date': fields.Date.today(),
                })
        return self.env["ir.actions.actions"]._for_xml_id("dxl_at_reordering_automation.action_reordering_report_line")
