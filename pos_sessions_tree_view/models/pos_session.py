from odoo import fields, models, api
from odoo.exceptions import UserError

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    bank_amount = fields.Float(string="Bank Amount", compute="get_payments")
    cash_amount = fields.Float(string="Cash Amount", compute="get_payments")
    online_payments_amount = fields.Float(string="Online Payments Amount")
    easypaisa_amount = fields.Float(string="EasyPaisa Amount")
    return_amount = fields.Float(string="Refund Amount", compute="_compute_return")
    discount_amount = fields.Float(string="Discount Amount", compute="_compute_return")

    def get_payments(self):
        cash_method = self.env['pos.payment.method'].search([('name', '=', 'Cash')])
        bank_method = self.env['pos.payment.method'].search([('name', '=', 'Bank')])
        online_payment_method = self.env['pos.payment.method'].search([('name', '=', 'Online Payment')])
        easypaisa_method = self.env['pos.payment.method'].search([('name', '=', 'Easy Paisa')])
        for rec in self:
            cash_total_amount = [payment.amount for payment in self.env['pos.payment'].search([('session_id', '=', rec.id), ('payment_method_id', 'in', cash_method.ids)])] if cash_method else []
            bank_total_amount = [payment.amount for payment in self.env['pos.payment'].search([('session_id', '=', rec.id), ('payment_method_id', 'in', bank_method.ids)])] if bank_method else []
            online_total_amount = [payment.amount for payment in self.env['pos.payment'].search([('session_id', '=', rec.id), ('payment_method_id', 'in', online_payment_method.ids)])] if online_payment_method else []
            easypaisa_total_amount = [payment.amount for payment in self.env['pos.payment'].search([('session_id', '=', rec.id), ('payment_method_id', 'in', easypaisa_method.ids)])] if easypaisa_method else []
            
            rec.cash_amount = sum(cash_total_amount)
            rec.bank_amount = sum(bank_total_amount)
            rec.online_payments_amount = sum(online_total_amount)
            rec.easypaisa_amount = sum(easypaisa_total_amount)
    
    def _compute_return(self):
        for rec in self:
            rec.discount_amount = 0
            rec.return_amount = 0
            for order in rec.order_ids:
                for line in order.lines:
                    rec.discount_amount += (line.discount/100) * (line.price_unit * line.qty)
                    rec.return_amount += (line.price_unit * line.refunded_qty)