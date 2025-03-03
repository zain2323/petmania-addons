# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        if not self.user_has_groups('restricts_security.group_restrict_contact_creation'):
            raise UserError("Sorry You Are Not Allowed To Create New Contacts.")
        return super(ResPartner, self).create(vals)
