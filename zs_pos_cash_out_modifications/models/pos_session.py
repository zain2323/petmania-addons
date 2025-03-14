from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    is_cashed_out = fields.Boolean(string="Is Cashed Out First?", default=False)
    is_cashed_out_last = fields.Boolean(string="Is Cashed Out Last?", default=False)


class EmployeeSecretKey(models.Model):
    _name = 'pos.employee.secret.key'
    _description = 'Employee Secret Keys for POS'

    name = fields.Char(string='Employee Name', required=True)
    secret_key = fields.Char(string='Secret Key', required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('secret_key_unique', 'UNIQUE(secret_key)', 'Secret Key must be unique!')
    ]

    @api.constrains('secret_key')
    def _check_secret_key(self):
        for record in self:
            if not record.secret_key:
                raise ValidationError(_("Secret Key cannot be empty!"))
