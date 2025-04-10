from odoo import fields, models, api, _
from datetime import datetime, time
import pytz

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter
import base64
import io
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class ProductAttributesReport(models.TransientModel):
    _name = 'product.attributes.report.wizard'

    report_file = fields.Binary('File Data')
    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')

    attribute_fields = [
        'company_type',
        'product_division_id',
        'categ_id',
        'product_brand_id',
        'ads_quarterly',
        'ads_half_year',
        'product_scm_grading_id',
        'product_attribute_1_id',
        'company_rank',
        'standard_price',
        'profit_value',
        'profit_percent',
        'list_price',
        'custom_uom_id',
        'uom_pricing',
        'taxes_id',
        'default_code',
        'barcode',
        'product_manufacture_id',
        'product_core_id',
        'product_procurement_type_id',
        'product_vendor_name_id',
        'product_packing_nature_id',
        'product_packing_type_id',
        'product_packsize_id',
        'product_attribute_2_id',
        'product_attribute_3_id',
        'product_pcs_in_a_tray',
        'minimum_ordering_qty',
        'product_type_id',
        'product_formula_id',
        'product_storage_id',
        'product_life_stage_id',
        'product_material_id',
    ]

    def action_generate_report(self):
        self._get_data_for_products()
        return {
            'name': 'Sales Analysis Report',
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=product.attributes.report.wizard&field=report_file&id=%s&filename=%s' % (
                self.id, 'Product Attributes Report.xlsx'),
            'target': 'self',
        }

    @api.model
    def get_attribute_fields_description(self):
        """Get a dictionary of field technical names and their display names"""
        result = {}
        product_product = self.env['product.product']

        for field_name in self.attribute_fields:
            try:
                field = product_product._fields[field_name]
                result[field_name] = field.string
            except KeyError:
                result[field_name] = field_name.replace('_', ' ').title()

        return result

    def _get_data_for_products(self):
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

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Attribute Completion')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3'
        })

        percentage_format = workbook.add_format({'num_format': '0.00%'})

        # Get attribute field descriptions
        field_descriptions = self.get_attribute_fields_description()
        # Setup headers
        row = 0
        col = 0

        # Product info columns
        worksheet.write(row, col, 'Product ID', header_format)
        worksheet.set_column(col, col, 10)
        col += 1

        worksheet.write(row, col, 'Product Name', header_format)
        worksheet.set_column(col, col, 40)
        col += 1

        # Attribute columns - one for each attribute
        for field_name in self.attribute_fields:
            worksheet.write(row, col, field_descriptions[field_name], header_format)
            worksheet.set_column(col, col, 15)
            col += 1

        # Summary columns
        worksheet.write(row, col, 'Filled', header_format)
        worksheet.set_column(col, col, 10)
        col += 1

        worksheet.write(row, col, 'Total', header_format)
        worksheet.set_column(col, col, 10)
        col += 1

        worksheet.write(row, col, 'Completion %', header_format)
        worksheet.set_column(col, col, 15)

        # Fill data rows
        row = 1
        for product in products:
            col = 0

            # Product info
            worksheet.write(row, col, product.id)
            col += 1

            worksheet.write(row, col, product.name)
            col += 1

            # Check each attribute
            filled_count = 0
            total_attributes = len(self.attribute_fields)

            for field_name in self.attribute_fields:
                try:
                    value = getattr(product, field_name)

                    # For Many2one fields, check if relation exists
                    if hasattr(value, 'id'):
                        has_value = bool(value.id)
                    else:
                        has_value = bool(value)

                    if has_value:
                        filled_count += 1
                        worksheet.write(row, col, 'Yes')
                    else:
                        worksheet.write(row, col, 'No')
                except AttributeError as e:
                    _logger.exception(str(e))
                    worksheet.write(row, col, 'N/A')

                col += 1

            # Summary info
            worksheet.write(row, col, filled_count)
            col += 1

            worksheet.write(row, col, total_attributes)
            col += 1

            completion_percentage = filled_count / total_attributes if total_attributes else 0
            worksheet.write(row, col, completion_percentage, percentage_format)

            row += 1
        workbook.close()

        self.report_file = base64.b64encode(output.getvalue())
