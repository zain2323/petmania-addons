from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ads_quarterly = fields.Char(string="ADS (3 Months)", company_dependent=True)
    ads_half_year = fields.Char(string="ADS (6 Months)", company_dependent=True)
    storage_config_id = fields.Many2one('min.max.config.storage', string='Min Config By Storage',
                                        compute="_compute_storage_config_id")
    value_config_id = fields.Many2one('min.max.config', string='Min Max Config By Value',
                                      compute="_compute_value_config_id")
    storage_config_basis = fields.Char(string='Storage Config Basis', compute='_compute_storage_config_id')
    value_config_basis = fields.Char(string='Value Config Basis', compute='_compute_value_config_id')

    def _compute_value_config_id(self):
        for rec in self:
            rec.value_config_id = False
            rec.value_config_basis = None
            value_config_franchise_division = rec.env['min.max.config'].search(
                [('franchise_division', '=', rec.company_type.id), ('product_id', '=', False), ('brand_id', '=', False),
                 ('product_category_id', '=', False), ('product_division', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_franchise_division and rec.company_type.id:
                rec.value_config_id = value_config_franchise_division.id
                rec.value_config_basis = "Franchise Division"
            # for product division
            value_config_product_division = rec.env['min.max.config'].search(
                [('product_division', '=', rec.product_division_id.id), ('product_id', '=', False),
                 ('brand_id', '=', False),
                 ('product_category_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_product_division and rec.product_division_id:
                rec.value_config_id = value_config_product_division.id
                rec.value_config_basis = "Product Division"

            # for product category
            value_config_category = rec.env['min.max.config'].search(
                [('product_category_id', '=', rec.categ_id.id), ('product_id', '=', False), ('brand_id', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_category and rec.categ_id.id:
                rec.value_config_id = value_config_category.id
                rec.value_config_basis = "Category"

            # for brand
            value_config_brand = rec.env['min.max.config'].search(
                [('brand_id', '=', rec.product_brand_id.id), ('product_id', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_brand and rec.product_brand_id.id:
                rec.value_config_id = value_config_brand.id
                rec.value_config_basis = "Brand"

            #  for product
            # find out the min and max days of the product by value and storage
            value_config_product = rec.env['min.max.config'].search(
                [('product_id', '=', rec.id), ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_product and rec.id:
                rec.value_config_id = value_config_product.id
                rec.value_config_basis = "Product"

    def _compute_storage_config_id(self):
        for rec in self:
            rec.storage_config_id = False
            rec.storage_config_basis = None
            # for franchise division
            storage_config_franchise_division = rec.env['min.max.config.storage'].search(
                [('franchise_division', '=', rec.company_type.id), ('product_id', '=', False), ('brand_id', '=', False),
                 ('product_category_id', '=', False), ('product_division', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_franchise_division and rec.company_type.id:
                rec.storage_config_id = storage_config_franchise_division.id
                rec.storage_config_basis = "Franchise Division"

            # for product division
            storage_config_product_division = rec.env['min.max.config.storage'].search(
                [('product_division', '=', rec.product_division_id.id), ('product_id', '=', False),
                 ('brand_id', '=', False),
                 ('product_category_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_product_division and rec.product_division_id.id:
                rec.storage_config_id = storage_config_product_division.id
                rec.storage_config_basis = "Product Division"

            # for product category
            storage_config_category = rec.env['min.max.config.storage'].search(
                [('product_category_id', '=', rec.categ_id.id), ('product_id', '=', False), ('brand_id', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_category and rec.categ_id.id:
                rec.storage_config_id = storage_config_category.id
                rec.storage_config_basis = "Category"

            # for brand
            storage_config_brand = rec.env['min.max.config.storage'].search(
                [('brand_id', '=', rec.product_brand_id.id), ('company_id', '=', self.env.company.id),
                 ('product_id', '=', False), ], limit=1)
            if storage_config_brand and rec.id:
                rec.storage_config_id = storage_config_brand.id
                rec.storage_config_basis = "Brand"

            # for product
            storage_config_product = rec.env['min.max.config.storage'].search(
                [('product_id', '=', rec.id), ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_product and rec.id:
                rec.storage_config_id = storage_config_product.id
                rec.storage_config_basis = "Product"

    def _calculate_ads(self, months):
        end_date = (datetime.now() + timedelta(hours=5)).date()
        n_days = 90 if months == 3 else 180
        start_date = end_date - timedelta(days=n_days)
        companies = self.env['res.company'].search([])
        for company in companies:
            query = """Select * from get_abc_sales_analysis_data_v2('%s','%s','%s','%s','%s','%s', '%s')""" % (
                {company.id}, {}, {}, {}, start_date, end_date, 'all')
            self._cr.execute(query)
            sales_data = self._cr.dictfetchall()
            for sales_dict in sales_data:
                try:
                    product_id = sales_dict.get('product_id')
                    sales_qty = sales_dict.get('sales_qty')
                    ads = round(sales_qty / n_days, 2)
                    product = self.env['product.product'].browse(product_id)
                    product_template_id = product.product_tmpl_id.id
                    product_tmpl = self.env['product.product'].browse(product_template_id).with_company(company)
                    if months == 3:
                        product_tmpl.ads_quarterly = ads
                    if months == 6:
                        product_tmpl.ads_half_year = ads
                except:
                    pass

    def _cron_calculate_ads(self):
        """This will calculate the ads based on 3 and 6 months and assign it to the respective fields"""
        # from respective reordering get its sales history for 3 and 6 months
        self._calculate_ads(3)
        self._calculate_ads(6)

    def _cron_assign_sales_contribution_class(self):
        """This will run and assign sales contribution class (aka abc category) based on the product division"""
        # loop over all the product divisions and find out all the relevant products.
        # for each division, compute the abc category and assign it in scc
        # if category is A -> set SCM to FS else FC
        end_date = datetime.now().date()
        start_date = date.today().replace(day=1) - relativedelta(months=3)

        product_divisions = self.env['product.division'].search([])
        for division in product_divisions:
            products = self.env['product.product'].search([('product_division_id', '=', division.id)])
            products = set(products.ids) or {}

            if not products:
                continue

            query = """
                            Select * from get_division_wise_abc_sales_analysis_data('%s','%s','%s','%s','%s','%s', '%s')
                        """ % (
                {}, products, {}, {}, start_date, end_date, 'all')
            print(query)
            self._cr.execute(query)
            sales_data = self._cr.dictfetchall()
            for product_dict in sales_data:
                product_id = product_dict['product_id']
                category = product_dict['analysis_category']
                scc = self.env['attribute.1'].search([('name', '=', category)])
                if not scc:
                    scc = self.env['attribute.1'].create({
                        'name': category,
                    })

                product = self.env['product.product'].browse(product_id)

                # assigning scc category
                product.product_tmpl_id.product_attribute_1_id = scc.id

                # checking if scm category is not trial
                if not product.product_tmpl_id.product_scm_grading_id.is_trial:
                    if scc.name == 'A':
                        scm_grading_name = 'FA (DAILY) CATEGORY'
                    # either B or C
                    else:
                        scm_grading_name = 'FC (WEEKLY) CATEGORY'

                    scm_grading = self.env['scm.grading'].search([('name', '=', scm_grading_name)])
                    if scm_grading:
                        product.product_tmpl_id.product_scm_grading_id = scm_grading.id
