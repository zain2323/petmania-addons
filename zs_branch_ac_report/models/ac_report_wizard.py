from odoo import models, fields, api
from datetime import date


class GenerateACReportWizard(models.TransientModel):
    _name = 'ac.generate.report.wizard'
    _description = 'Generate AC Machine Report Wizard'

    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)

    def action_generate_report(self):
        DailyReport = self.env['ac.daily.machine.report']

        # Check if report exists for this date and company
        existing_report = DailyReport.search([
            ('report_date', '=', self.report_date),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if existing_report:
            # Open existing report
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ac.daily.machine.report',
                'res_id': existing_report.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Create new report
            new_report = DailyReport.create({
                'report_date': self.report_date,
                'company_id': self.env.company.id,
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ac.daily.machine.report',
                'res_id': new_report.id,
                'view_mode': 'form',
                'target': 'current',
            }