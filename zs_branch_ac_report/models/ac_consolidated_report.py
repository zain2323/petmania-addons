from odoo import models, fields, api
import base64
from io import BytesIO
import xlsxwriter
from datetime import date, timedelta


class ConsolidatedACMachineReport(models.Model):
    _name = 'ac.consolidated.machine.report'
    _description = 'Consolidated AC Machine Status Report'

    name = fields.Char(string='Report Name', required=True,
                       default=lambda self: 'Machine Report - ' + fields.Date.today().strftime('%Y-%m-%d'))
    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)
    file_data = fields.Binary(string='Excel Report')
    file_name = fields.Char(string='File Name')

    @api.model
    def generate_consolidated_report(self):
        """Method to be called by cron job"""
        yesterday = (date.today() + timedelta(hours=5)) - timedelta(days=1)
        report = self.create({
            'name': f'Machine Report - {yesterday.strftime("%Y-%m-%d")}',
            'report_date': yesterday,
        })
        report.generate_excel_report()
        return True

    def generate_excel_report(self):
        """Generate Excel report with machine status across all branches"""
        # Create workbook and worksheet
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('AC Machine Status Report')

        # Add formatting
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 16})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        summary_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#E0E0E0', 'border': 1})
        bold_format = workbook.add_format({'bold': True, 'border': 1})

        # Updated color formats as per request
        operational_format = workbook.add_format({'bg_color': '#00FF00', 'border': 1, 'align': 'center'})  # Green
        not_operational_format = workbook.add_format({'bg_color': '#FF0000', 'border': 1, 'align': 'center'})  # Red
        not_available_format = workbook.add_format({'bg_color': '#FFFF00', 'border': 1, 'align': 'center'})  # Yellow
        available_not_submitted_format = workbook.add_format(
            {'bg_color': '#FFA500', 'border': 1, 'align': 'center'})  # Orange

        # Get all machines and ONLY companies that have machines configured
        MachineConfig = self.env['ac.machine.config']
        machines = MachineConfig.search([])

        # Get only companies that have at least one machine
        company_ids = machines.mapped('company_id.id')
        companies = self.env['res.company'].browse(company_ids)

        unique_machines = set(machines.mapped('name'))

        # Add report title
        worksheet.merge_range(0, 0, 0, len(companies), 'AC Equipment Maintenance Report', title_format)

        # Set up headers
        worksheet.write(2, 0, 'Machine', header_format)
        for col, company in enumerate(companies, 1):
            worksheet.write(2, col, company.name, header_format)
        worksheet.write(2, len(companies) + 1, 'Summary', header_format)

        # Get daily reports for the report date
        DailyReport = self.env['ac.daily.machine.report']
        daily_reports = DailyReport.search([('report_date', '=', self.report_date)])

        # Organize data as a lookup dictionary for easy access
        report_data = {}
        for report in daily_reports:
            company_id = report.company_id.id
            report_data[company_id] = {}
            for line in report.line_ids:
                report_data[company_id][line.machine_id.name] = {
                    'operational_status': line.operational_status,
                }

        # Initialize counters for column summaries
        column_counts = {}
        for company in companies:
            column_counts[company.id] = {
                'OP': 0,  # Operational
                'NOP': 0,  # Not Operational
                'NA': 0,  # Not Available
                'AR': 0,  # Available/Report not submitted
            }

        # Initialize counters for row summaries
        row_counts = {}

        # Fill in machine data
        row = 3  # Start from row 3 after the title and header
        for machine_name in sorted(unique_machines):
            worksheet.write(row, 0, machine_name, cell_format)

            # Initialize row summary
            row_counts[machine_name] = {
                'OP': 0,  # Operational
                'NOP': 0,  # Not Operational
                'NA': 0,  # Not Available
                'AR': 0,  # Available/Report not submitted
            }

            for col, company in enumerate(companies, 1):
                # Find machine in this company
                machine = MachineConfig.search([
                    ('name', '=', machine_name),
                    ('company_id', '=', company.id)
                ], limit=1)

                status_text = ""
                cell_format_to_use = cell_format

                if machine:
                    availability = machine.status

                    # Check if we have operational data for this machine/company
                    if company.id in report_data and machine_name in report_data[company.id]:
                        operational = report_data[company.id][machine_name]['operational_status']

                        if availability == "available" and operational == "operational":
                            cell_format_to_use = operational_format  # Green
                            status_text = "Operational"
                            column_counts[company.id]['OP'] += 1
                            row_counts[machine_name]['OP'] += 1
                        elif availability == "available" and operational == "not_operational":
                            status_text = "Not Operational"
                            cell_format_to_use = not_operational_format  # Red
                            column_counts[company.id]['NOP'] += 1
                            row_counts[machine_name]['NOP'] += 1
                        elif availability == "not_available":
                            status_text = "Not Available"
                            cell_format_to_use = not_available_format  # Yellow
                            column_counts[company.id]['NA'] += 1
                            row_counts[machine_name]['NA'] += 1
                    else:
                        # Just show availability if no operational data
                        status_text = "Available/Report not submitted"
                        cell_format_to_use = available_not_submitted_format
                        column_counts[company.id]['AR'] += 1
                        row_counts[machine_name]['AR'] += 1
                else:
                    status_text = "Not Available"
                    cell_format_to_use = not_available_format  # Yellow
                    column_counts[company.id]['NA'] += 1
                    row_counts[machine_name]['NA'] += 1

                worksheet.write(row, col, status_text, cell_format_to_use)

            # Write row summary
            row_summary = []
            if row_counts[machine_name]['OP'] > 0:
                row_summary.append(f"OP-{row_counts[machine_name]['OP']}")
            if row_counts[machine_name]['NOP'] > 0:
                row_summary.append(f"NOP-{row_counts[machine_name]['NOP']}")
            if row_counts[machine_name]['NA'] > 0:
                row_summary.append(f"NA-{row_counts[machine_name]['NA']}")
            if row_counts[machine_name]['AR'] > 0:
                row_summary.append(f"AR-{row_counts[machine_name]['AR']}")

            worksheet.write(row, len(companies) + 1, ", ".join(row_summary), bold_format)

            row += 1

        # Write column summaries
        worksheet.write(row, 0, 'Summary', summary_format)
        for col, company in enumerate(companies, 1):
            col_summary = []
            if column_counts[company.id]['OP'] > 0:
                col_summary.append(f"OP-{column_counts[company.id]['OP']}")
            if column_counts[company.id]['NOP'] > 0:
                col_summary.append(f"NOP-{column_counts[company.id]['NOP']}")
            if column_counts[company.id]['NA'] > 0:
                col_summary.append(f"NA-{column_counts[company.id]['NA']}")
            if column_counts[company.id]['AR'] > 0:
                col_summary.append(f"AR-{column_counts[company.id]['AR']}")

            worksheet.write(row, col, ", ".join(col_summary), summary_format)

        # Add legend
        legend_row = row + 2
        worksheet.write(legend_row, 0, 'Legend:', bold_format)
        worksheet.write(legend_row, 1, 'OP = Operational', operational_format)
        worksheet.write(legend_row, 2, 'NOP = Not Operational', not_operational_format)
        worksheet.write(legend_row, 3, 'NA = Not Available', not_available_format)
        worksheet.write(legend_row, 4, 'AR = Available/Report not submitted', available_not_submitted_format)

        # Adjust column widths
        worksheet.set_column(0, 0, 25)  # Machine name column
        worksheet.set_column(1, len(companies), 20)  # Company columns
        worksheet.set_column(len(companies) + 1, len(companies) + 1, 25)  # Summary column

        workbook.close()

        # Save the report to the record
        self.write({
            'file_data': base64.b64encode(output.getvalue()),
            'file_name': f'machine_status_report_{self.report_date}.xlsx'
        })