from odoo import fields, models, api, _
from datetime import datetime, time
import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class BranchConfigStorageData(models.TransientModel):
    _name = 'branch.config.storage.data'
    _description = 'Branch Storage Configuration Data'

    wizard_id = fields.Many2one('branch.storage.config.report.wizard', string='Wizard', required=True,
                                ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', required=True)
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    barcode = fields.Char(string='Barcode')
    cost = fields.Char(string='Cost')
    storage_config_id = fields.Many2one('min.max.config.storage', string='Storage Configuration')
    basis_of_configuration = fields.Char(string='Basis of Configuration')
    reordering_id = fields.Many2one('stock.warehouse.orderpoint', string='Reordering Rule')
    min_qty = fields.Char(string='Min QTY')
    max_qty = fields.Char(string='Max QTY')
    range = fields.Char(string='Range')
    ads = fields.Char(string='ads')


class BranchStorageConfigurationReportWizard(models.TransientModel):
    _name = 'branch.storage.config.report.wizard'

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
            'name': 'Min Max Configuration By Storage - Report',
            'res_model': 'branch.config.storage.data',
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
            min_qty = "N/A"
            max_qty = "N/A"

            reordering_rule = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', product.id), ('company_id', '=', self.env.company.id)], limit=1)
            ads = float(max(float(product.ads_quarterly or 0), float(product.ads_half_year or 0)))
            range = ""
            if product.storage_config_id:
                min_qty = product.storage_config_id.min_days * ads
                max_qty = product.storage_config_id.max_days * ads
                range = f'{product.storage_config_id.min_days}-{product.storage_config_id.max_days}'

            products_dict.append({
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'barcode': product.barcode,
                'cost': product.standard_price,
                'reordering_id': reordering_rule.id,
                'storage_config_id': product.storage_config_id.id,
                'basis_of_configuration': product.storage_config_basis,
                'ads': ads,
                'min_qty': min_qty,
                'max_qty': max_qty,
                'range': range,
                'company_id': self.env.company.id,
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        pivot_model = self.env['branch.config.storage.data']
        pivot_model.search([('company_id', '=', self.env.company.id)]).unlink()
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
                'reordering_id': product_data['reordering_id'],
                'storage_config_id': product_data['storage_config_id'],
                'basis_of_configuration': product_data['basis_of_configuration'],
                'ads': product_data['ads'],
                'range': product_data['range'],
                'min_qty': product_data['min_qty'],
                'max_qty': product_data['max_qty'],
                'company_id': product_data['company_id'],
            })
