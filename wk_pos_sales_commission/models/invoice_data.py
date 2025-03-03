# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import Warning,ValidationError
from datetime import timedelta
import datetime

class InvoiceData(models.TransientModel):
    _name = 'invoice.data'
    _description = "Invoice Data"

    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    report_of = fields.Selection([
            ('employee', 'Employee'),
            ('user', 'User'),
            ], string='Report of', default='employee', required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="User")

    @api.constrains('start_date', 'end_date')
    def check_dates(self): 
        if(self.start_date and self.end_date):
            if(self.end_date < self.end_date):
                raise ValidationError('Start Date Cannot be smaller than End Date')
