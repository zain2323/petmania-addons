from odoo import http
from odoo.http import content_disposition, request
import base64
import json
from odoo.tools import html_escape
import io
import xlsxwriter
from collections import defaultdict
from odoo.exceptions import UserError

SELECTION_DICT = {
    'consu': 'Consumable',
    'service': 'Service',
    'product': 'Storable Product'
}

class InvoiceExcelReportController(http.Controller):
    @http.route([
       '/accounting/locationwise/excel_report/',
   ], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, report_id=None, **args):
        response = request.make_response(
           None,
           headers=[
               ('Content-Type', 'application/vnd.ms-excel'),
               ('Content-Disposition', content_disposition('product-locations-report' + '.xlsx'))
           ]
       )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_row_format = workbook.add_format({'bold': True})

        #get data for the report.
        products = request.env['product.template'].search([])
        internal_locations = request.env['stock.location'].search([('usage', '=', 'internal')])
        locations_qty = defaultdict(list)
        for product in products:
            quant_search_domain = [('product_tmpl_id', '=', product.id), ('quantity', '>', 0), ('location_id', 'in', internal_locations.ids)]
            grouped_results = request.env['stock.quant'].read_group(
            domain=quant_search_domain,
            fields=['location_id', 'quantity:sum'],
            groupby=['location_id']
            )
            for grouped_result in grouped_results:
                locations_qty[product.id].append({"qty": grouped_result.get('quantity'), 'location': request.env['stock.location'].browse(grouped_result.get('location_id')[0]).complete_name})
        #prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("invoices")
        sheet.write(0, 0, 'No.', header_row_format)
        sheet.write(0, 1, 'Favourite', header_row_format)
        sheet.write(0, 2, 'Name', header_row_format)
        sheet.write(0, 3, 'Brand', header_row_format)
        sheet.write(0, 4, 'Internal Reference', header_row_format)
        sheet.write(0, 5, 'Responsible', header_row_format)
        sheet.write(0, 6, 'Barcode', header_row_format)
        sheet.write(0, 7, 'Company', header_row_format)
        sheet.write(0, 8, 'Sales Price', header_row_format)
        sheet.write(0, 9, 'Cost', header_row_format)
        sheet.write(0, 10, 'Product Category', header_row_format)
        sheet.write(0, 11, 'Product Type', header_row_format)
        sheet.write(0, 12, 'Quantity On Hand', header_row_format)
        sheet.write(0, 13, 'Forecasted Quantity', header_row_format)
        # Writing internal locations
        header_col = 14
        internal_locations_dict = {}
        for loc in internal_locations:
            sheet.write(0, header_col, loc.complete_name, header_row_format)
            internal_locations_dict[loc.complete_name] = header_col
            header_col += 1
        
        row = 1
        number = 1
        for product in products:
           sheet.write(row, 0, number)
           sheet.write(row, 1, 'Favourite')
           sheet.write(row, 2, product['name'])
           sheet.write(row, 3, product['product_brand_id']['name']) # Add brand
           sheet.write(row, 4, product['default_code'])
           sheet.write(row, 5, product['name']) #responsible
           sheet.write(row, 6, product['barcode'])
           sheet.write(row, 7, product['company_id']['name'])
           sheet.write(row, 8, product['list_price'])
           sheet.write(row, 9, product['standard_price'])
           sheet.write(row, 10, product['categ_id']['complete_name'])
           sheet.write(row, 11, self.get_selection_field_label(product['detailed_type']))
           sheet.write(row, 12, product['qty_available'])
           sheet.write(row, 13, product['virtual_available'])
           locations = locations_qty[product.id]
           for location in locations:
                sheet.write(row, internal_locations_dict.get(location['location']), location['qty'])
           row += 1
           number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
    
    def get_selection_field_label(self, key):
        return SELECTION_DICT.get(key)