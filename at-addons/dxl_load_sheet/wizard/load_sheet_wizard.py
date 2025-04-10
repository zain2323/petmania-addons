# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, exceptions, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LoadSheetWizard(models.TransientModel):
    _name = "load.sheet.wizard"
    _description = "Load Sheet Wizard"

    sale_order_ids = fields.Many2many('sale.order')
    warning_msg = fields.Html(string="Warning", readonly=True)

    def proceed(self):
        self.sale_order_ids.generate_load_sheet()
