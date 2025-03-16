from odoo import fields, models, api, _
from datetime import datetime, time
import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class CustomerSalesData(models.TransientModel):
    _name = 'inventory.planning.data'
    _description = 'Inventory Planning Data'

    wizard_id = fields.Many2one('inventory.planning.report.wizard', string='Wizard', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    franchise_name = fields.Char(string='Franchise Division')
    division_name = fields.Char(string='Product Division')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    barcode = fields.Char(string='Barcode')
    cost = fields.Char(string='Cost')
    selected_method = fields.Char(string='Selected Method')
    min_qty = fields.Integer(string='Min QTY')
    min_investment = fields.Float(string='Min Investment')
    max_qty = fields.Integer(string='Max QTY')
    max_investment = fields.Float(string='Max Investment')


class CustomerWiseSalesAnalysisReport(models.TransientModel):
    _name = 'inventory.planning.report.wizard'

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
            'name': 'Inventory Planning Report',
            'res_model': 'inventory.planning.data',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('wizard_id', '=', self.id)],
        }

    def _get_data_for_products(self):
        # update reordering rules data
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
            reordering_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id), ('company_id', '=', self.env.company.id)], limit=1)

            if reordering_rule:
                max_qty_by_value = reordering_rule.max_qty_by_value

                max_qty_by_storage = reordering_rule.max_qty_by_storage

                if max_qty_by_storage > max_qty_by_value:
                    selected_method = "ADS"
                else:
                    selected_method = "Value"

                min_qty = reordering_rule.product_min_qty
                max_qty = reordering_rule.product_max_qty

                min_investment = min_qty * product.standard_price
                max_investment = max_qty * product.standard_price
            else:
                selected_method = "N/A"
                min_qty = 0
                max_qty = 0
                min_investment = 0
                max_investment = 0

            products_dict.append({
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'barcode': product.barcode,
                'cost': product.standard_price,
                'selected_method': selected_method,
                'min_qty': min_qty,
                'min_investment': min_investment,
                'max_qty': max_qty,
                'max_investment': max_investment,
                'company_id': self.env.company.id,
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        pivot_model = self.env['inventory.planning.data']
        pivot_model.search([('wizard_id', '=', self.id), ('company_id', '=', self.env.company.id)]).unlink()
        for product_data in products_data:
            pivot_model.create({
                'wizard_id': self.id,
                'product_name': product_data['product_name'],
                'franchise_name': product_data['franchise_name'],
                'division_name': product_data['division_name'],
                'category_name': product_data['category_name'],
                'brand_name': product_data['brand_name'],
                'barcode': product_data['barcode'],
                'cost': product_data['cost'],
                'selected_method': product_data['selected_method'],
                'min_qty': product_data['min_qty'],
                'min_investment': product_data['min_investment'],
                'max_qty': product_data['max_qty'],
                'max_investment': product_data['max_investment'],
                'company_id': product_data['company_id'],
            })
