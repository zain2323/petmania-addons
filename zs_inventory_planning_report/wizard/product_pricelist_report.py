from collections import defaultdict

from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
import pytz
import re

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter

import logging

_logger = logging.getLogger(__name__)


class ProductPricelistData(models.TransientModel):
    _name = 'product.pricelist.data'
    _description = 'Product pricelist data'

    wizard_id = fields.Many2one('product.pricelist.report.wizard', string='Wizard', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    product_id = fields.Many2one('product.product', string='Product Id')
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    sale_price = fields.Float(string='Sale Price')
    cost_price = fields.Float(string='Cost Price')
    margin = fields.Float(string='Margin')
    income_account_id = fields.Many2one('account.account', string="Income Account")
    expense_account_id = fields.Many2one('account.account', string="Expense Account")


class ProductPricelistReportWizard(models.TransientModel):
    _name = 'product.pricelist.report.wizard'

    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    def action_view_pivot(self):
        self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Pricelist Report',
            'res_model': 'product.pricelist.data',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('wizard_id', '=', self.id)],
        }

    def _filter_pricelist_by_product(self, item_ids, product_id):
        item = item_ids.filtered(lambda i: i.product_tmpl_id.id == product_id)
        return item

    def convert_currency_to_float(self, amount_str):
        cleaned_str = re.sub(r"[^\d.]", "", amount_str)

        if cleaned_str.count('.') > 1:
            cleaned_str = cleaned_str.rstrip('.')

        return float(cleaned_str) if cleaned_str else 0.0  # Convert to float

    def _get_data_for_products(self):
        domain = []
        item_ids = self.pricelist_id.item_ids
        _logger.critical([i.product_tmpl_id for i in item_ids])
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
            item = self._filter_pricelist_by_product(item_ids, product.product_tmpl_id.id)
            if len(item) > 0:
                item = item[0]
                # raise UserError(f"{product.name} has multiple prices set in the specified pricelist")
            sale_price =  self.convert_currency_to_float(item.price) if item else 0
            cost_price = product.standard_price
            _logger.critical(sale_price)
            margin = sale_price - cost_price

            income_account_id = None
            expense_account_id = None
            if product.categ_id:
                income_account_id = product.categ_id.property_account_income_categ_id.id
                expense_account_id = product.categ_id.property_account_expense_categ_id.id

            products_dict.append({
                'product_id': product.id,
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'sale_price': sale_price,
                'cost_price': cost_price,
                'margin': margin,
                'income_account_id': income_account_id,
                'expense_account_id': expense_account_id,
                'company_id': self.env.company.id,
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        pivot_model = self.env['product.pricelist.data']
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
                'sale_price': product_data['sale_price'],
                'cost_price': product_data['cost_price'],
                'margin': product_data['margin'],
                'income_account_id': product_data['income_account_id'],
                'expense_account_id': product_data['expense_account_id'],
                'company_id': product_data['company_id'],
            })
