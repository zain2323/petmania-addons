from odoo import fields, models, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.setu_abc_analysis_reports.library import xlsxwriter
import base64
from io import BytesIO
import logging
import numpy as np
from . import setu_excel_formatter as formatter

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class SetuABCSalesAnalysisReport(models.TransientModel):
    _name = 'sales.analysis.report.wizard'

    stock_file_data = fields.Binary('Stock Movement File')
    start_date = fields.Date('Start Date')
    months_before = fields.Integer('Before Months')

    def get_sales(self, branch, from_date, company_type, previous_months=0):
        # Iterate over the last `previous_months` months, including the current month
        sales_data = {
            'branch': branch.name if company_type != "Petmania Clinic" else branch.clinic_company_name
        }
        # get todays sale
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        # current_date = local_tz.fromutc(datetime(2024, 9,2)).date()
        current_date = local_tz.fromutc(datetime.now()).date()
        previous_date = current_date - timedelta(days=1)
        today_sales = self._get_branch_sales(branch, previous_date, previous_date, company_type)
        _logger.critical(str(today_sales))

        sales_data["today_sales"] = today_sales
        # avg target per day
        sales_data['avg_target_per_day'] = branch.avg_target_per_day_sale_store if 'store' in company_type.lower() else branch.avg_target_per_day_sale_clinic

        # get month wise sales
        for i in range(previous_months + 1):
            # Calculate the start and end date for the previous month
            month_start_date = (from_date - relativedelta(months=i)).replace(day=1)
            next_month_start_date = (month_start_date + relativedelta(months=1)).replace(day=1) - timedelta(days=1)

            # Check if the month_start_date is in the current month
            if month_start_date.year == current_date.year and month_start_date.month == current_date.month:
                # If it's the current month, set the month_end_date to current day - 1
                month_end_date = previous_date
            else:
                # Otherwise, set it to the last day of the month
                month_end_date = next_month_start_date

            # Get sales for this specific month
            sales = self._get_branch_sales(branch, month_start_date, month_end_date, company_type)
            sales_data[f"{month_start_date.strftime('%B %Y')}"] = sales

        return sales_data

    def _get_branch_sales(self, branch, from_date, end_date, company_type):
        company_type = company_type.lower()
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        local_date_start = local_tz.localize(datetime.combine(from_date, datetime.min.time()))  # Start of the day
        # Set the time for end_date to 23:59:59
        local_date_end = local_tz.localize(datetime.combine(end_date, datetime.max.time()))  # End of the day

        # Convert to UTC
        utc_date_start = local_date_start.astimezone(pytz.utc)
        utc_date_end = local_date_end.astimezone(pytz.utc)
        n_days = (end_date - from_date).days + 1
        if n_days < 0:
            n_days = abs(n_days)
        elif n_days == 0:
            n_days += 1

        sale_orders = self.env['sale.order'].search([
            ('create_date', '>=', utc_date_start),
            ('create_date', '<=', utc_date_end),
            ('company_id', '=', branch.id),
            ('state', 'in', ['sale', 'done'])
        ])
        sale_total = 0
        for sale_order in sale_orders:
            for line in sale_order.order_line:
                if line.product_id.company_type and line.product_id.company_type.name.lower() != company_type:
                    continue
                sale_total += line.price_subtotal

        # Get all pos orders within the date range
        pos_orders = self.env['pos.order'].search([
            ('date_order', '>=', utc_date_start),
            ('date_order', '<=', utc_date_end),
            ('company_id', '=', branch.id),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])


        pos_total = 0
        for order in pos_orders:
            for line in order.lines:
                if line.product_id.company_type and line.product_id.company_type.name.lower() != company_type:
                    continue
                pos_total += line.price_subtotal_incl
        _logger.critical("Start Date: " + str(from_date))
        _logger.critical("End Date: " + str(end_date))

        total_sales = pos_total / n_days
        return {
            'sale_total': sale_total,
            'pos_total': pos_total,
            'total_sales': total_sales,
            'total_sales_without_avg': pos_total
        }

    def transform_sales_data(self, sales_dict, from_date):
        current_month = from_date.strftime('%B %Y')
        columns = ['branches', 'today_sales', 'avg_target_per_day']
        months = set()
        sales_data = {
            "branch_data": {}
        }
        for branch_info in sales_dict:
            for key in branch_info:
                try:
                    # parsing the key to date if it succeeds then for sure it is a month
                    datetime.strptime(key, '%B %Y')
                    if key == current_month:
                        sales_data['branch_data'][f"{key}-sales"] = []
                        months.add(f"{key}")
                    sales_data['branch_data'][key] = []
                    months.add(key)
                except:
                    pass
        for col in columns:
            sales_data['branch_data'][col] = []
        for branch_info in sales_dict:
            branch_name = branch_info['branch']
            today_sales = branch_info['today_sales']['total_sales']
            avg_target_per_day = branch_info['avg_target_per_day']
            sales_data["branch_data"]["branches"].append(branch_name)
            sales_data["branch_data"]["today_sales"].append(today_sales)
            sales_data["branch_data"]["avg_target_per_day"].append(avg_target_per_day)

            for month in months:
                if month == f"{current_month}" and month in branch_info:
                    sales_data['branch_data'][f"{month}-sales"].append(branch_info[f"{month}"]['total_sales_without_avg'])
                if month in branch_info:
                    sales_data['branch_data'][month].append(branch_info[month]['total_sales'])
        return sales_data

    def get_sales_analysis_report_data(self, company_type):
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        from_date = self.start_date
        # current_date = local_tz.fromutc(datetime(2024, 9, 2)).date()
        current_date = local_tz.fromutc(datetime.now()).date()
        if  current_date == from_date:
            from_date = from_date - timedelta(days=1)
        companies = self.env['res.company'].search([('include_in_sales_report', '=', True)])
        branches = []
        todays_sale = []
        for company in companies:
            sales = self.get_sales(company, from_date, previous_months=self.months_before, company_type=company_type)
            branches.append(company.name)
            todays_sale.append(sales)
        sales_data = self.transform_sales_data(todays_sale, from_date)
        return sales_data

    def download_report(self):
        file_name = "Sales Analysis Report.xlsx"
        store_sales = self.get_sales_analysis_report_data(company_type="Petmania Store")['branch_data']

        # Prepare the data manually for writing in xlsxwriter
        reordered_columns = ['Branch', 'Average Target per Day', 'Today Sales',]
        store_sales = {
            'Branch': store_sales['branches'],
            'Average Target per Day': store_sales['avg_target_per_day'],
            'Today Sales': store_sales['today_sales'],
            **{k: v for k, v in store_sales.items() if k not in ['branches', 'today_sales', 'avg_target_per_day']}
        }

        # Prepare the Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Sheet1')

        # Define formats
        columns_format = workbook.add_format(formatter.ODD_FONT_MEDIUM_BOLD_CENTER)
        bold_format = workbook.add_format(formatter.FONT_MEDIUM_BOLD_LEFT)
        bold_format_with_border = workbook.add_format(formatter.FONT_MEDIUM_BOLD_LEFT_BORDER)
        title_format = workbook.add_format(formatter.FONT_BIG_CENTER)
        subheading_format = workbook.add_format(formatter.FONT_MEDIUM_CENTER)
        number_format = workbook.add_format(formatter.FONT_MEDIUM_NUMBER_FORMAT)
        number_format_without_border = workbook.add_format(formatter.FONT_MEDIUM_NUMBER_FORMAT_WITHOUT_BORDER)
        number_format_yellow = workbook.add_format(formatter.FONT_MEDIUM_NUMBER_FORMAT_YELLOW)
        number_format_green = workbook.add_format(formatter.FONT_MEDIUM_NUMBER_FORMAT_GREEN)
        number_format_red = workbook.add_format(formatter.FONT_MEDIUM_NUMBER_FORMAT_RED)

        # Write the report title
        title = "Daily Sales Report PETMANIA STORES & Clinics"
        worksheet.merge_range('A1:G2', title, title_format)

        worksheet.merge_range('A3:G3', 'Daily Petmania Store Sales', subheading_format)
        row_idx = 4
        # Write the header row (row 3, 0-indexed)
        header_row = reordered_columns + ["Average Sale of " + key if 'sales' not in key else 'Total Sale of ' + key.split('-')[0] for key in store_sales.keys() if key not in reordered_columns]
        worksheet.write_row(4, 0, header_row, columns_format)

        # Apply bold format to the first column (Branches)
        # worksheet.set_column('A:A', None, bold_format)

        # Prepare data for transposition
        data = np.array([store_sales[key] for key in store_sales.keys() if len(store_sales[key]) > 0])
        transposed_data = data.T  # Transpose the data for proper row-wise writing

        # Write data rows starting from row 4
        row_idx += 2
        for row in transposed_data:
            for col_idx, value in enumerate(row):
                # Apply number format if the value is numeric
                if col_idx >= 1:
                    value = float(value)
                    format_sales = number_format
                    if col_idx == 4:
                        prev_sales = float(row[col_idx + 1])
                        # green if < 5% of last month sale
                        if value < prev_sales - (prev_sales * 0.05):
                            format_sales = number_format_red
                        # green if > 5% of last month sale
                        elif value > prev_sales + (prev_sales * 0.05):
                            format_sales = number_format_green
                        else:
                            format_sales = number_format_yellow
                    worksheet.write_number(row_idx, col_idx, float(value), format_sales)
                else:
                    worksheet.write(row_idx, col_idx, value, bold_format_with_border)
            row_idx += 1
        # Grand total
        worksheet.write(row_idx, 0, 'Grand Total', bold_format)
        # Calculate vertical sum for numeric columns
        numeric_data = transposed_data[:, 1:].astype(float)
        vertical_sums = numeric_data.sum(axis=0)
        for col_idx, total in enumerate(vertical_sums, start=1):
            worksheet.write_number(row_idx, col_idx, total, number_format_without_border)

        row_idx += 2
        # Clinic Sales
        worksheet.merge_range(row_idx, 0, row_idx, 6, 'Daily Petmania Clinic Sales', subheading_format)
        row_idx += 2
        clinic_sales = self.get_sales_analysis_report_data(company_type="Petmania Clinic")['branch_data']
        clinic_sales = {
            'Branches': clinic_sales['branches'],
            'Average Target per Day': clinic_sales['avg_target_per_day'],
            'Today Sales': clinic_sales['today_sales'],
            **{k: v for k, v in clinic_sales.items() if k not in ['branches', 'today_sales', 'avg_target_per_day']}
        }
        # Prepare data for transposition
        data = np.array([clinic_sales[key] for key in clinic_sales.keys() if len(clinic_sales[key]) > 0])
        transposed_data = data.T  # Transpose the data for proper row-wise writing

        for row in transposed_data:
            for col_idx, value in enumerate(row):
                # Apply number format if the value is numeric
                if col_idx >= 1:
                    value = float(value)
                    format_sales = number_format
                    if col_idx == 4:
                        prev_sales = float(row[col_idx + 1])
                        # green if < 5% of last month sale
                        if value < prev_sales - (prev_sales * 0.05):
                            format_sales = number_format_red
                        # green if > 5% of last month sale
                        elif value > prev_sales + (prev_sales * 0.05):
                            format_sales = number_format_green
                        else:
                            format_sales = number_format_yellow
                    worksheet.write_number(row_idx, col_idx, float(value), format_sales)
                else:
                    worksheet.write(row_idx, col_idx, value, bold_format_with_border)
            row_idx += 1

        # Grand total
        worksheet.write(row_idx, 0, 'Grand Total', bold_format)
        # Calculate vertical sum for numeric columns
        numeric_data = transposed_data[:, 1:].astype(float)
        vertical_sums = numeric_data.sum(axis=0)
        for col_idx, total in enumerate(vertical_sums, start=1):
            worksheet.write_number(row_idx, col_idx, total, number_format_without_border)

        # Closing the workbook
        workbook.close()

        # Convert to base64 and store in stock_file_data
        output.seek(0)
        file_data = base64.b64encode(output.read())
        self.write({'stock_file_data': file_data})
        output.close()
        return {
            'name': 'Sales Analysis Report',
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=sales.analysis.report.wizard&field=stock_file_data&id=%s&filename=%s' % (
                self.id, file_name),
            'target': 'self',
        }