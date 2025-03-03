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
    _name = 'customer.sales.data'
    _description = 'Customer Sales Data'

    wizard_id = fields.Many2one('customer.sales.analysis.wizard', string='Wizard', required=True)
    customer_name = fields.Char(string='Customer Name')
    city = fields.Char(string='City')
    channel = fields.Char(string='Channel')
    captain = fields.Char(string='Captain')
    backup_captain = fields.Char(string='Backup Captain')
    brand_name = fields.Char(string='Brand Name')
    sales = fields.Float(string='Sales')
    brand_purchase_count = fields.Float(string='Brand Purchase Count')
    order_count = fields.Integer(string='Order Count', group_operator="max")
    drop_size_avg = fields.Float(string='Drop Size Avg', group_operator="max")
    brand_coverage = fields.Float(string='Brand Coverage', group_operator="max")


class CustomerWiseSalesAnalysisReport(models.TransientModel):
    _name = 'customer.sales.analysis.wizard'

    file_data = fields.Binary('File Data')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    customer_ids = fields.Many2many('res.partner', string='Customers')
    city_ids = fields.Many2many('res.city', string='City')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    captain_ids = fields.Many2many('customer.order.booker', string='Captains')
    report_type = fields.Selection([
        ('customer_wise', 'Brand Wise Sales'), ('brand_wise', 'Brand Wise Coverage'),
        ('numeric_coverage', 'Numeric Coverage'),
    ], string='Report Type', default='customer_wise', required=True)

    def action_view_pivot(self):
        self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Sales Analysis',
            'res_model': 'customer.sales.data',
            'view_mode': 'pivot',
            'target': 'current',
            'context': {'search_default_wizard_id': self.id},
        }

    def _get_data_for_brand_wise_sales(self):
        # Compute total net sales by customer with optional customer filter
        domain = [
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]

        if self.customer_ids:
            domain.append(('partner_id', 'in', self.customer_ids.ids))

        if self.captain_ids:
            domain.append(('partner_id.order_booker_id', 'in', self.captain_ids.ids))
        if self.city_ids:
            domain += ['|'] * (len(self.city_ids) - 1)
            for city in self.city_ids:
                domain.append(('partner_id.city', 'ilike', city.name))

        invoices = self.env['account.move'].search(domain)
        all_brands = set()
        sales_data = {}
        for invoice in invoices:
            customer_name = invoice.partner_id.name if invoice.partner_id else 'Undefined Customer'
            channel = invoice.partner_id.type_id.name if invoice.partner_id.type_id else ''
            captain = invoice.partner_id.order_booker_id.name if invoice.partner_id.order_booker_id else ''
            backup_captain = invoice.partner_id.backup_captain.name if invoice.partner_id.backup_captain else ''
            city = invoice.partner_id.city if invoice.partner_id.city else ""

            lines = invoice.invoice_line_ids
            if self.product_brand_ids:
                lines = lines.filtered(lambda l: l.product_id.product_brand_id.id in self.product_brand_ids.ids)
            if self.product_category_ids:
                lines = lines.filtered(lambda l: l.product_id.categ_id.id in self.product_category_ids.ids)

            if not lines:
                continue


            if customer_name not in sales_data:
                sales_data[customer_name] = {
                    'customer_name': customer_name,
                    'city': city,
                    'channel': channel,
                    'captain': captain,
                    'backup_captain': backup_captain,
                    'order_count': 1 if invoice.move_type == 'out_invoice' else 0,
                }
            else:
                sales_data[customer_name]['order_count'] += 1 if invoice.move_type == 'out_invoice' else 0

            for line in lines:
                brand_name = line.product_id.product_brand_id.name if line.product_id.product_brand_id else 'Undefined Brand'
                amount = line.price_subtotal
                count = 1

                if line.move_id.move_type in ['out_refund']:
                    amount = amount * -1
                    count = -1

                if brand_name not in sales_data[customer_name]:
                    sales_data[customer_name][brand_name] = {
                        "amount": amount,
                        "count": count,
                        "brand_purchase_count": set([(line.move_id.id, line.product_id.product_brand_id.id)]),
                    }
                else:
                    if brand_name in sales_data[customer_name]:
                        sales_data[customer_name][brand_name]["count"] += count
                        sales_data[customer_name][brand_name]["amount"] += amount
                        sales_data[customer_name][brand_name]["brand_purchase_count"].add(
                            (line.move_id.id, line.product_id.product_brand_id.id))
                        # if line.move_id.move_type not in ['out_refund']:
                        #     sales_data[customer_name][brand_name]["brand_purchase_count"].add((line.move_id.id, line.product_id.product_brand_id.id))
                        # else:
                        #     sales_data[customer_name][brand_name]["brand_refund_count"].add((line.move_id.id, line.product_id.product_brand_id.id))
                    else:
                        sales_data[customer_name][brand_name]['amount'] = amount
                        sales_data[customer_name][brand_name]['count'] = count
                        sales_data[customer_name][brand_name]['brand_purchase_count'] = set([(line.move_id.id, line.product_id.product_brand_id.id)])

                all_brands.add(brand_name)

        return sales_data, all_brands

    def _get_data_for_brand_wise_coverage(self):
        # Compute total net sales by customer with optional customer filter
        domain = [
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]

        if self.customer_ids:
            domain.append(('partner_id', 'in', self.customer_ids.ids))

        if self.captain_ids:
            domain.append(('partner_id.order_booker_id', 'in', self.captain_ids.ids))
        if self.city_ids:
            domain += ['|'] * (len(self.city_ids) - 1)
            for city in self.city_ids:
                domain.append(('partner_id.city', 'ilike', city.name))

        invoices = self.env['account.move'].search(domain)
        all_brands = set()
        sales_data = {}
        for invoice in invoices:
            customer_name = invoice.partner_id.name if invoice.partner_id else 'Undefined Customer'
            channel = invoice.partner_id.type_id.name if invoice.partner_id.type_id else ''
            captain = invoice.partner_id.order_booker_id.name if invoice.partner_id.order_booker_id else ''
            backup_captain = invoice.partner_id.backup_captain.name if invoice.partner_id.backup_captain else ''
            city = invoice.partner_id.city if invoice.partner_id.city else ""

            lines = invoice.invoice_line_ids
            if self.product_brand_ids:
                lines = lines.filtered(lambda l: l.product_id.product_brand_id.id in self.product_brand_ids.ids)
            if self.product_category_ids:
                lines = lines.filtered(lambda l: l.product_id.categ_id.id in self.product_category_ids.ids)

            if not lines:
                continue

            if customer_name not in sales_data:
                sales_data[customer_name] = {
                    'customer_name': customer_name,
                    'city': city,
                    'channel': channel,
                    'captain': captain,
                    'backup_captain': backup_captain,
                }

            for line in lines:
                brand_name = line.product_id.product_brand_id.name if line.product_id.product_brand_id else 'Undefined Brand'
                if brand_name not in sales_data[customer_name]:
                    sales_data[customer_name][brand_name] = set([(line.move_id.id, line.product_id.product_brand_id.id)])

                else:
                    if brand_name in sales_data[customer_name]:
                        sales_data[customer_name][brand_name].add(
                            (line.move_id.id, line.product_id.product_brand_id.id))
                    else:
                        sales_data[customer_name][brand_name] = set([(line.move_id.id, line.product_id.product_brand_id.id)])

                all_brands.add(brand_name)

        return sales_data, all_brands

    def _get_data_for_numeric_coverage(self):
        # Compute total net sales by customer with optional customer filter
        domain = [
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]

        if self.customer_ids:
            domain.append(('partner_id', 'in', self.customer_ids.ids))

        if self.captain_ids:
            domain.append(('partner_id.order_booker_id', 'in', self.captain_ids.ids))
        if self.city_ids:
            domain += ['|'] * (len(self.city_ids) - 1)
            for city in self.city_ids:
                domain.append(('partner_id.city', 'ilike', city.name))

        invoices = self.env['account.move'].search(domain)
        all_brands = set()
        sales_data = {}
        for invoice in invoices:
            customer_name = invoice.partner_id.name if invoice.partner_id else 'Undefined Customer'
            channel = invoice.partner_id.type_id.name if invoice.partner_id.type_id else ''
            captain = invoice.partner_id.order_booker_id.name if invoice.partner_id.order_booker_id else ''
            backup_captain = invoice.partner_id.backup_captain.name if invoice.partner_id.backup_captain else ''
            city = invoice.partner_id.city if invoice.partner_id.city else ""

            lines = invoice.invoice_line_ids
            if self.product_brand_ids:
                lines = lines.filtered(lambda l: l.product_id.product_brand_id.id in self.product_brand_ids.ids)
            if self.product_category_ids:
                lines = lines.filtered(lambda l: l.product_id.categ_id.id in self.product_category_ids.ids)

            if not lines:
                continue

            if customer_name not in sales_data:
                sales_data[customer_name] = {
                    'customer_name': customer_name,
                    'city': city,
                    'channel': channel,
                    'captain': captain,
                    'backup_captain': backup_captain,
                }

            for line in lines:
                brand_name = line.product_id.product_brand_id.name if line.product_id.product_brand_id else 'Undefined Brand'
                if brand_name not in sales_data[customer_name]:
                    sales_data[customer_name][brand_name] = 1
                all_brands.add(brand_name)

            # assigning missing brands to zero
            for customer, customer_data in sales_data.items():
                for brand in all_brands:
                    if brand not in customer_data:
                        sales_data[customer][brand] = 0

        return sales_data, all_brands

    def generate_brand_wise_coverage(self):
        # File name and data retrieval
        file_name = "Customer Brand Wise Coverage Report.xlsx"
        sales_data, all_brands = self._get_data_for_brand_wise_coverage()
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Brand Wise Coverage')

        header_format = workbook.add_format({'bold': True, 'align': 'center'})
        data_format = workbook.add_format({'align': 'left'})

        title = "Customer Brand Wise Coverage"
        worksheet.merge_range('A1:G2', title, header_format)

        # writing start and end date
        worksheet.write(2, 0, 'Start Date', header_format)
        worksheet.write(2, 1, self.start_date.strftime('%m/%d/%Y'))
        worksheet.write(3, 0, 'End Date', header_format)
        worksheet.write(3, 1, self.end_date.strftime('%m/%d/%Y'))

        worksheet.write(4, 0, 'Customer', header_format)
        worksheet.write(4, 1, 'City', header_format)
        worksheet.write(4, 2, 'Channel', header_format)
        worksheet.write(4, 3, 'Captain', header_format)
        worksheet.write(4, 4, 'Backup Captain', header_format)

        col = 5
        brand_columns = {}

        # doing this so undefined brand is at last
        try:
            all_brands.remove("Undefined Brand")
            all_brands = sorted(all_brands)
            all_brands.append("Undefined Brand")
        except Exception:
            pass

        for brand in all_brands:
            worksheet.write(4, col, brand, header_format)
            brand_columns[brand] = col
            col += 1

        # Write data rows for each customer
        row = 5
        for customer_data in sales_data.values():
            worksheet.write(row, 0, customer_data['customer_name'], data_format)
            worksheet.write(row, 1, customer_data['city'], data_format)
            worksheet.write(row, 2, customer_data['channel'], data_format)
            worksheet.write(row, 3, customer_data['captain'], data_format)
            worksheet.write(row, 4, customer_data['backup_captain'], data_format)

            for brand, sales in customer_data.items():
                if brand not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain']:
                    worksheet.write(row, brand_columns[brand], len(sales), data_format)

            row += 1

        # Close the workbook
        workbook.close()

        # Convert to base64 and store in stock_file_data
        output.seek(0)
        file_data = base64.b64encode(output.read())
        self.write({'file_data': file_data})
        output.close()
        return file_name

    def generate_numeric_coverage(self):
        # File name and data retrieval
        file_name = "Customer Brand Wise Numeric Coverage Report.xlsx"
        sales_data, all_brands = self._get_data_for_numeric_coverage()
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Numeric Coverage')

        header_format = workbook.add_format({'bold': True, 'align': 'center'})
        data_format = workbook.add_format({'align': 'left'})

        title = "Numeric Coverage"
        worksheet.merge_range('A1:G2', title, header_format)

        # writing start and end date
        worksheet.write(2, 0, 'Start Date', header_format)
        worksheet.write(2, 1, self.start_date.strftime('%m/%d/%Y'))
        worksheet.write(3, 0, 'End Date', header_format)
        worksheet.write(3, 1, self.end_date.strftime('%m/%d/%Y'))

        worksheet.write(4, 0, 'Customer', header_format)
        worksheet.write(4, 1, 'City', header_format)
        worksheet.write(4, 2, 'Channel', header_format)
        worksheet.write(4, 3, 'Captain', header_format)
        worksheet.write(4, 4, 'Backup Captain', header_format)

        col = 5
        brand_columns = {}

        # doing this so undefined brand is at last
        try:
            all_brands.remove("Undefined Brand")
            all_brands = sorted(all_brands)
            all_brands.append("Undefined Brand")
        except Exception:
            pass

        for brand in all_brands:
            worksheet.write(4, col, brand, header_format)
            brand_columns[brand] = col
            col += 1

        # Write data rows for each customer
        row = 5
        for customer_data in sales_data.values():
            worksheet.write(row, 0, customer_data['customer_name'], data_format)
            worksheet.write(row, 1, customer_data['city'], data_format)
            worksheet.write(row, 2, customer_data['channel'], data_format)
            worksheet.write(row, 3, customer_data['captain'], data_format)
            worksheet.write(row, 4, customer_data['backup_captain'], data_format)

            for brand, sales in customer_data.items():
                if brand not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain']:
                    worksheet.write(row, brand_columns[brand], sales, data_format)

            row += 1

        # Close the workbook
        workbook.close()

        # Convert to base64 and store in stock_file_data
        output.seek(0)
        file_data = base64.b64encode(output.read())
        self.write({'file_data': file_data})
        output.close()
        return file_name

    def generate_customer_wise_sales(self):
        # File name and data retrieval
        file_name = "Customer Wise Sales Analysis Report.xlsx"
        sales_data, all_brands = self._get_data_for_brand_wise_sales()
        # raise UserError(str(sales_data))
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Sales Report')

        header_format = workbook.add_format({'bold': True, 'align': 'center'})
        data_format = workbook.add_format({'align': 'left'})

        title = "Customer Sales Analysis Report"
        worksheet.merge_range('A1:G2', title, header_format)

        # writing start and end date
        worksheet.write(2, 0, 'Start Date', header_format)
        worksheet.write(2, 1, self.start_date.strftime('%m/%d/%Y'))
        worksheet.write(3, 0, 'End Date', header_format)
        worksheet.write(3, 1, self.end_date.strftime('%m/%d/%Y'))

        worksheet.write(4, 0, 'Customer', header_format)
        worksheet.write(4, 1, 'City', header_format)
        worksheet.write(4, 2, 'Channel', header_format)
        worksheet.write(4, 3, 'Captain', header_format)
        worksheet.write(4, 4, 'Backup Captain', header_format)
        worksheet.write(4, 5, 'Total Sales', header_format)

        col = 6
        brand_columns = {}

        # doing this so undefined brand is at last
        try:
            all_brands.remove("Undefined Brand")
            all_brands = sorted(all_brands)
            all_brands.append("Undefined Brand")
        except Exception:
            pass

        for brand in all_brands:
            worksheet.write(4, col, f'{brand} - Amount', header_format)
            worksheet.write(4, col+1, f'{brand} - Count', header_format)
            brand_columns[brand] = col
            col += 2
        worksheet.write(4, col, 'Order Count', header_format)
        worksheet.write(4, col + 1, 'Drop Size (Average)', header_format)
        worksheet.write(4, col + 2, 'Brand Coverage (%)', header_format)

        # Write data rows for each customer
        row = 5
        for customer_data in sales_data.values():
            total_sales = sum(
                value['amount'] for key, value in customer_data.items() if
                key not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain', 'order_count']
            )
            worksheet.write(row, 0, customer_data['customer_name'], data_format)
            worksheet.write(row, 1, customer_data['city'], data_format)
            worksheet.write(row, 2, customer_data['channel'], data_format)
            worksheet.write(row, 3, customer_data['captain'], data_format)
            worksheet.write(row, 4, customer_data['backup_captain'], data_format)
            worksheet.write(row, 5, total_sales, data_format)

            brands_covered = 0
            for key, value in customer_data.items():
                if key not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain', 'order_count']:
                    worksheet.write(row, brand_columns[key], value['amount'], data_format)
                    purchase_count = len(value['brand_purchase_count'])
                    worksheet.write(row, brand_columns[key] + 1, purchase_count, data_format)
                    brands_covered += 1
            worksheet.write(row, col, customer_data['order_count'], data_format)
            avg_drop_size = round(total_sales / customer_data['order_count'] if customer_data['order_count'] > 0 else 0,2)

            # domain_brand = [('id', 'in', self.product_brand_ids.ids)] if self.product_brand_ids else []
            # n_brands = len(self.env['product.brand'].search(domain_brand))
            n_brands = len(self.env['product.brand'].search([]))
            brand_coverage = round((brands_covered / n_brands) * 100 if n_brands > 0 else 0, 2)

            worksheet.write(row, col + 1, avg_drop_size, data_format)
            worksheet.write(row, col + 2, brand_coverage, data_format)

            row += 1

        # Close the workbook
        workbook.close()

        # Convert to base64 and store in stock_file_data
        output.seek(0)
        file_data = base64.b64encode(output.read())
        self.write({'file_data': file_data})
        output.close()
        return file_name

    def populate_pivot_data(self):
        sales_data, all_brands = self._get_data_for_brand_wise_sales()
        pivot_model = self.env['customer.sales.data']
        domain_brand = [('id', 'in', self.product_brand_ids.ids)] if self.product_brand_ids else []
        n_brands = len(self.env['product.brand'].search(domain_brand))
        pivot_model.search([]).unlink()
        for customer_data in sales_data.values():
            total_sales = sum(
                value['amount'] for key, value in customer_data.items() if
                key not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain', 'order_count']
            )
            brands_covered = 0
            pivot_records = []
            for key, sales_obj in customer_data.items():
                if key not in ['customer_name', 'city', 'channel', 'captain', 'backup_captain', 'order_count']:
                    brands_covered += 1
                    rec = pivot_model.create({
                        'wizard_id': self.id,
                        'customer_name': customer_data['customer_name'],
                        'city': customer_data['city'],
                        'channel': customer_data['channel'],
                        'captain': customer_data['captain'],
                        'backup_captain': customer_data['backup_captain'],
                        'brand_name': key,
                        'sales': sales_obj['amount'],
                        'brand_purchase_count': len(sales_obj['brand_purchase_count']),
                        'order_count': customer_data['order_count'],
                    })
                    pivot_records.append(rec)
            # adding drop size in all pivot records
            for pivot_record in pivot_records:
                pivot_record.drop_size_avg = round(total_sales / customer_data['order_count'] if customer_data['order_count'] > 0 else 0,2)
                pivot_record.brand_coverage = round((brands_covered / n_brands) * 100 if n_brands > 0 else 0, 2)

    def download_report(self):
        if self.report_type == 'customer_wise':
            file_name = self.generate_customer_wise_sales()
        elif self.report_type == 'brand_wise':
            file_name = self.generate_brand_wise_coverage()
        elif self.report_type == 'numeric_coverage':
            file_name = self.generate_numeric_coverage()
        else:
            raise UserError("Invalid report type")
        return {
            'name': 'Sales Analysis Report',
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=customer.sales.analysis.wizard&field=file_data&id=%s&filename=%s' % (
                self.id, file_name),
            'target': 'self',
        }
