from collections import defaultdict

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter

import logging

_logger = logging.getLogger(__name__)


class OutOfStockData(models.TransientModel):
    _name = 'out.of.stock.data'
    _description = 'Branch out of stock data'

    wizard_id = fields.Many2one('out.of.stock.report.wizard', string='Wizard', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    product_id = fields.Many2one('product.product', string='Product Id')
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    min_qty = fields.Integer(string='Min QTY')
    qty_available = fields.Integer(string='Available QTY')
    out_of_stock_qty = fields.Integer(string='Out Of Stock QTY')
    ads = fields.Float(string='ADS')
    sale_loss = fields.Float(string="Sale Loss")
    scm_grading = fields.Char(string="SCM Grading")


class OutOfStockReportWizard(models.TransientModel):
    _name = 'out.of.stock.report.wizard'

    file_data = fields.Binary('File Data')
    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')

    def action_view_pivot(self):
        self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Out Of Stock Report',
            'res_model': 'out.of.stock.data',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('wizard_id', '=', self.id)],
        }

    def _get_data_for_products(self):
        rules = self.env['stock.warehouse.orderpoint'].search([('company_id', '=', self.env.company.id)])
        for rule in rules:
            rule._compute_product_min_max_qty()

        domain = []

        if self.franchise_division_ids:
            domain.append(('company_type', 'in', self.franchise_division_ids.ids))

        if self.product_division_ids:
            domain.append(('product_division_id', 'in', self.product_division_ids.ids))

        if self.product_category_ids:
            domain.append(('categ_id', 'in', self.product_category_ids.ids))

        if self.product_brand_ids:
            domain.append(('product_brand_id', 'in', self.product_brand_ids.ids))

        if self.product_ids:
            domain.append(('id', 'in', self.product_ids.ids))

        products = self.env['product.product'].search(domain)
        products_dict = []
        for product in products:
            reordering_rule = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', product.id), ('company_id', '=', self.env.company.id)], limit=1)
            qty_available = product.qty_available
            if reordering_rule:
                min_qty = reordering_rule.product_min_qty
                out_of_stock_qty = min_qty - qty_available
            else:
                min_qty = 0
                out_of_stock_qty = 0
            if out_of_stock_qty <= 0:
                continue
            ads = max(float(product.ads_quarterly or 0), float(product.ads_half_year or 0))
            sale_price = product.list_price or 0
            products_dict.append({
                'product_id': product.id,
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'min_qty': min_qty,
                'qty_available': qty_available,
                'out_of_stock_qty': out_of_stock_qty,
                'ads': ads,
                'sale_loss': ads * sale_price,
                'scm_grading': product.product_scm_grading_id.name,
                'company_id': self.env.company.id,
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        pivot_model = self.env['out.of.stock.data']
        pivot_model.search([('company_id', '=', self.env.company.id)]).unlink()
        for product_data in products_data:
            pivot_model.create({
                'wizard_id': self.id,
                'product_id': product_data['product_id'],
                'product_name': product_data['product_name'],
                'franchise_name': product_data['franchise_name'],
                'division_name': product_data['division_name'],
                'category_name': product_data['category_name'],
                'brand_name': product_data['brand_name'],
                'min_qty': product_data['min_qty'],
                'qty_available': product_data['qty_available'],
                'out_of_stock_qty': product_data['out_of_stock_qty'],
                'company_id': product_data['company_id'],
                'ads': product_data['ads'],
                'sale_loss': product_data['sale_loss'],
                'scm_grading': product_data['scm_grading'],
            })
