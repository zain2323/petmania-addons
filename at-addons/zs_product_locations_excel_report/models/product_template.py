# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date
from datetime import datetime, timedelta


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    def print_xlsx_locations_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/accounting/locationwise/excel_report',
            'target': 'new',
        }