# models/machine_config.py
from odoo import models, fields, api


class ACMachineConfig(models.Model):
    _name = 'ac.machine.config'
    _description = 'AC Machine Configuration'

    name = fields.Char('Machine Name', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available')
    ], string='Availability Status', required=True, default='available')
    company_id = fields.Many2one('res.company', string='Branch', required=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_ac_machine_company', 'UNIQUE(name, company_id)',
         'AC Machine name must be unique per branch!')
    ]