from odoo import http
from odoo.http import content_disposition, request
import base64
import json
from odoo.tools import html_escape
import io
import xlsxwriter
from collections import defaultdict
from odoo.exceptions import UserError

class InvoiceExcelReportController(http.Controller):
   @http.route([
       '/accounting/products/grammage/excel_report/',
   ], type='http', auth="user", csrf=False)
   def get_products_grammage_reports(self, report_id=None, **args):
        response = request.make_response(
           None,
           headers=[
               ('Content-Type', 'application/vnd.ms-excel'),
               ('Content-Disposition', content_disposition('product-grammage-report' + '.xlsx'))
           ]
       )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_row_format = workbook.add_format({'bold': True})
        #get data for the report.
        products = request.env['product.template'].search([])
        
        #prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("invoices")
        sheet.write(0, 0, 'S.No', header_row_format)
        sheet.write(0, 1, 'SKU', header_row_format)
        sheet.write(0, 2, 'Brand', header_row_format)
        sheet.write(0, 3, 'Product', header_row_format)
        sheet.write(0, 4, 'Category', header_row_format)
        sheet.write(0, 5, 'Price', header_row_format)
        sheet.write(0, 6, 'Weight in KG', header_row_format)
        sheet.write(0, 7, 'Rate Per KG', header_row_format)
        sheet.write(0, 8, 'Weight in G', header_row_format)
        sheet.write(0, 9, 'Rate Per Grammage', header_row_format)
        
        row = 1
        number = 1
        for product in products:
            weight_kg = product['weight']
            weight_g = weight_kg * 1000
            price = product['list_price']
            price_per_kg = price / weight_kg if weight_kg > 0 else 0
            price_per_g = price / weight_g if weight_g > 0 else 0
            
            sheet.write(row, 0, number)
            sheet.write(row, 1, product['default_code'])
            sheet.write(row, 2, product['product_brand_id']['name']) # Treating as a brand for now
            sheet.write(row, 3, product['name'])
            sheet.write(row, 4, product['categ_id']['complete_name'])
            sheet.write(row, 5, price)
            sheet.write(row, 6, weight_kg)
            sheet.write(row, 7, price_per_kg)
            sheet.write(row, 8, weight_g)
            sheet.write(row, 9, price_per_g)
           
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response