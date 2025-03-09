from collections import defaultdict

from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter

import logging

_logger = logging.getLogger(__name__)


class ProductAccountData(models.TransientModel):
    _name = 'product.account.data'
    _description = 'Product account data'

    wizard_id = fields.Many2one('product.account.report.wizard', string='Wizard', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    product_id = fields.Many2one('product.product', string='Product Id')
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    quantity = fields.Float(string='Quantity')
    sale_price = fields.Float(string='Sale Price')
    cost_price = fields.Float(string='Cost Price')
    margin = fields.Float(string='Margin')
    income_account_id = fields.Many2one('account.account', string="Income Account")
    expense_account_id = fields.Many2one('account.account', string="Expense Account")


class OutOfStockReportWizard(models.TransientModel):
    _name = 'product.account.report.wizard'

    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_view_pivot(self):
        self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Account Report',
            'res_model': 'product.account.data',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('wizard_id', '=', self.id)],
        }

    def _get_data_for_products(self):
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        local_date_start = local_tz.localize(datetime.combine(self.start_date, datetime.min.time()))  # Start of the day
        local_date_end = local_tz.localize(datetime.combine(self.end_date, datetime.max.time()))  # End of the day

        # Convert to UTC
        utc_start_date = local_date_start.astimezone(pytz.utc)
        utc_end_date = local_date_end.astimezone(pytz.utc)

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

        sessions = self.env['pos.session'].search([
            ('state', '=', 'closed'),
            ('company_id', '=', self.env.company.id),
            ('stop_at', '<=', utc_end_date),
            ('stop_at', '>=', utc_start_date),
        ])
        pos_orders = self.env['pos.order'].search([
            ('session_id', 'in', sessions.ids),
            ('company_id', '=', self.env.company.id),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])
        products = defaultdict(lambda: defaultdict(float))
        for order in pos_orders:
            lines = order.lines
            if self.franchise_division_ids:
                lines = lines.filtered(lambda l: l.product_id.company_type.id in self.franchise_division_ids.ids)
            if self.product_division_ids:
                lines = lines.filtered(lambda l: l.product_id.product_division_id.id in self.product_division_ids.ids)
            if self.product_category_ids:
                lines = lines.filtered(lambda l: l.product_id.categ_id.id in self.product_category_ids.ids)
            if self.product_brand_ids:
                lines = lines.filtered(lambda l: l.product_id.product_brand_id.id in self.product_brand_ids.ids)
            if self.product_ids:
                lines = lines.filtered(lambda l: l.product_id.id in self.product_ids.ids)
            for line in lines:
                products[line.product_id]['cost'] += line.total_cost
                products[line.product_id]['sales'] += line.price_subtotal
                products[line.product_id]['quantity'] += line.qty
                products[line.product_id]['margin'] += line.margin

        products_dict = []
        for product, data in products.items():
            sale_price = data['sales']
            cost_price = data['cost']
            quantity = data['quantity']
            margin = data['margin']
            margin_percent = data['margin_percent']
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
                'quantity': quantity,
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
        pivot_model = self.env['product.account.data']
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
                'quantity': product_data['quantity'],
                'sale_price': product_data['sale_price'],
                'cost_price': product_data['cost_price'],
                'margin': product_data['margin'],
                'income_account_id': product_data['income_account_id'],
                'expense_account_id': product_data['expense_account_id'],
                'company_id': product_data['company_id'],
            })
