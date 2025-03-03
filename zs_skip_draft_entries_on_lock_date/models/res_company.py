from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning

class ResCompany(models.Model):
    _inherit = "res.company"

    def _validate_fiscalyear_lock(self, values):
        if values.get('fiscalyear_lock_date'):
            return
        return super(ResCompany, self)._validate_fiscalyear_lock(values)