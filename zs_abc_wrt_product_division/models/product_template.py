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
