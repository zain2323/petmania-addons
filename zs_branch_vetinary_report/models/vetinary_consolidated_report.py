from odoo import models, fields, api
import base64
from io import BytesIO
import xlsxwriter
from datetime import date, timedelta


class ConsolidatedMachineReport(models.Model):
    _name = 'vet.consolidated.machine.report'
    _description = 'Consolidated Machine Status Report'

    name = fields.Char(string='Report Name', required=True,
                       default=lambda self: 'Machine Report - ' + fields.Date.today().strftime('%Y-%m-%d'))
    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)
    file_data = fields.Binary(string='Excel Report')
    file_name = fields.Char(string='File Name')

    @api.model
    def generate_consolidated_report(self):
        """Method to be called by cron job"""
        yesterday = date.today() - timedelta(days=1)
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
        worksheet = workbook.add_worksheet('Machine Status Report')

        # Add formatting
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        operational_format = workbook.add_format({'bg_color': '#90EE90', 'border': 1, 'align': 'center'})  # Light green
        not_operational_format = workbook.add_format(
            {'bg_color': '#FFA07A', 'border': 1, 'align': 'center'})  # Light salmon
        available_format = workbook.add_format({'bg_color': '#ADD8E6', 'border': 1, 'align': 'center'})  # Light blue
        not_available_format = workbook.add_format(
            {'bg_color': '#FFB6C1', 'border': 1, 'align': 'center'})  # Light pink

        # Get all machines and companies
        MachineConfig = self.env['vet.machine.config']
        companies = self.env['res.company'].search([])
        machines = MachineConfig.search([])
        unique_machines = set(machines.mapped('name'))

        # Set up headers
        worksheet.write(0, 0, 'Machine', header_format)
        for col, company in enumerate(companies, 1):
            worksheet.write(0, col, company.name, header_format)

        # Get daily reports for the report date
        DailyReport = self.env['vet.daily.machine.report']
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

        # Fill in machine data
        row = 1
        for machine_name in sorted(unique_machines):
            worksheet.write(row, 0, machine_name, cell_format)

            for col, company in enumerate(companies, 1):
                # Find machine in this company
                machine = MachineConfig.search([
                    ('name', '=', machine_name),
                    ('company_id', '=', company.id)
                ], limit=1)

                status_text = ""
                cell_format_to_use = cell_format

                if machine:
                    availability = "Available" if machine.status == "available" else "Not Available"

                    # Check if we have operational data for this machine/company
                    if company.id in report_data and machine_name in report_data[company.id]:
                        operational = "Operational" if report_data[company.id][machine_name][
                                                           'operational_status'] == 'operational' else "Not Operational"
                        status_text = f"{operational}/{availability}"

                        # Select format based on status
                        if operational == "Operational" and availability == "Available":
                            cell_format_to_use = operational_format
                        elif operational == "Not Operational":
                            cell_format_to_use = not_operational_format
                        elif availability == "Not Available":
                            cell_format_to_use = not_available_format
                    else:
                        # Just show availability if no operational data
                        status_text = f"No Report/{availability}"
                        cell_format_to_use = available_format if availability == "Available" else not_available_format
                else:
                    status_text = "N/A"

                worksheet.write(row, col, status_text, cell_format_to_use)

            row += 1

        # Adjust column widths
        worksheet.set_column(0, 0, 25)  # Machine name column
        worksheet.set_column(1, len(companies), 20)  # Company columns

        workbook.close()

        # Save the report to the record
        self.write({
            'file_data': base64.b64encode(output.getvalue()),
            'file_name': f'machine_status_report_{self.report_date}.xlsx'
        })