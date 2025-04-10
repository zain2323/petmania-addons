# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    unit_price_company_curr = fields.Float()
    exchange_rate = fields.Float()


    @api.onchange('move_id.currency_id','product_qty','price_unit')
    def onchange_method_currency_id(self):
        if self.price_unit and self.currency_id:
            if self.currency_id.id != self.env.company.currency_id.id:
                rates = self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id)])[0]
                self.unit_price_company_curr = self.price_unit * rates.inverse_company_rate
                self.exchange_rate = rates.inverse_company_rate
            else:
                self.unit_price_company_curr = self.price_unit
                self.exchange_rate = 1

    def cal_exchange_rate(self):
        if self.price_unit and self.currency_id:
            if self.currency_id.id != self.env.company.currency_id.id:
                rates = self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id), ('name', "<=", self.create_date.date())])
                if rates:
                    self.unit_price_company_curr = self.price_unit * rates[0].inverse_company_rate
                    self.exchange_rate = rates[0].inverse_company_rate
                else:
                    self.unit_price_company_curr = self.price_unit
                    self.exchange_rate = 1
            else:
                self.unit_price_company_curr = self.price_unit
                self.exchange_rate = 1


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('currency_id')
    def onchange_method_currency_id(self):
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                line.onchange_method_currency_id()

    def action_post(self):
        res = super(AccountMove, self).action_post()
        print(22222222222)
        self.onchange_method_currency_id()
        return res



