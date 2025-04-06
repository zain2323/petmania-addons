from odoo import models, fields, api
from datetime import date


class DailyACMachineReport(models.Model):
    _name = 'ac.daily.machine.report'
    _description = 'Daily AC Machine Status Report'
    _rec_name = 'report_date'
    _order = 'report_date desc'

    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)
    user_id = fields.Many2one('res.users', string='Branch Manager', required=True,
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Branch', required=True,
                                 default=lambda self: self.env.company)
    line_ids = fields.One2many('ac.daily.machine.report.line', 'report_id', string='Machines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ], string='Status', default='draft', required=True)

    _sql_constraints = [
        ('unique_ac_report_date_company', 'UNIQUE(report_date, company_id)',
         'Only one report per day per branch is allowed!')
    ]

    def action_submit(self):
        return self.write({'state': 'submitted'})

    @api.model
    def create(self, vals):
        record = super(DailyACMachineReport, self).create(vals)
        if not record.line_ids:
            record.generate_report_lines()
        return record

    def generate_report_lines(self):
        MachineConfig = self.env['ac.machine.config']
        ReportLine = self.env['ac.daily.machine.report.line']

        for report in self:
            # Get all available machines for this branch
            machines = MachineConfig.search([('company_id', '=', report.company_id.id), ('active', '=', True)])

            for machine in machines:
                ReportLine.create({
                    'report_id': report.id,
                    'machine_id': machine.id,
                    'operational_status': 'operational',
                })


class DailyACMachineReportLine(models.Model):
    _name = 'ac.daily.machine.report.line'
    _description = 'Daily AC Machine Report Line'

    report_id = fields.Many2one('ac.daily.machine.report', string='Report', required=True, ondelete='cascade')
    machine_id = fields.Many2one('ac.machine.config', string='Machine', required=True)
    operational_status = fields.Selection([
        ('operational', 'Operational'),
        ('not_operational', 'Not Operational')
    ], string='Operational Status', required=True, default='operational')
    availability_status = fields.Selection(related='machine_id.status', string='Availability Status', readonly=True)
    remarks = fields.Char(string='Remarks')

    @api.depends('report_id.state')
    def _compute_readonly(self):
        for line in self:
            line.readonly = line.report_id.state == 'submitted'

    readonly = fields.Boolean(compute='_compute_readonly', store=True)