# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pos_commission_id = fields.Many2one(
        'pos.commission', string="POS Commission")


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        result = super().write(vals)
        if result and self:
            for rec in self:
                move_id = rec.search([('name', '=', rec.ref)], limit=1)
                if move_id and move_id.payment_state == 'paid':
                    for line in move_id.invoice_line_ids:
                        line.pos_commission_id.write({"state": "paid"})
        return result

# class AccountPaymentInherit(models.Model):
#     _inherit = 'account.payment'

#     def post(self):
#         result = super(AccountPaymentInherit,self).post()
#         if result:
#             move_id = self.invoice_ids[0]
#             for line in move_id.invoice_line_ids:
#                 if(move_id.invoice_payment_state == "paid"):
#                     line.pos_commission_id.write({"state":"paid"})
#         return result
