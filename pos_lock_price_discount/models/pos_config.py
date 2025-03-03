# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    lock_discount = fields.Boolean(string="Lock discount", default=False)
    discount_password = fields.Char(string=u"Password")

    @api.constrains('discount_password')
    def check_discount_password(self):
        if self.lock_discount is True:
            for item in str(self.discount_password):
                try:
                    int(item)
                except Exception as e:
                    raise ValidationError(_("The unlock discount password should be a number"))
