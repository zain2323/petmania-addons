from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    payment_lines = fields.One2many('pos.payment.line', 'session_id', string='Payment Lines')

    def write(self, vals):
        """ Override write method to generate payment lines when session state is closed """
        res = super(PosSession, self).write(vals)

        # Check if the session is being closed
        if 'state' in vals and vals['state'] == 'closed':
            for session in self:
                session._generate_payment_lines()

        return res

    def _generate_payment_lines(self):
        """ Helper method to generate aggregated payment lines when session closes """
        for rec in self:
            rec.payment_lines.unlink()

            payments = rec.env['pos.payment'].search([('session_id', '=', rec.id)])

            payment_lines_dict = {}
            for payment in payments:
                payment_method = payment.payment_method_id.name
                if payment_method not in payment_lines_dict:
                    payment_lines_dict[payment_method] = {'session_id': rec.id, 'amount': payment.amount}
                else:
                    payment_lines_dict[payment_method]['amount'] += payment.amount

            # Create payment lines
            lines = []
            for key, value in payment_lines_dict.items():
                lines.append((0, 0, {
                    'amount': value['amount'],
                    'session_id': value['session_id'],
                    'payment_method': key
                }))

            if lines:
                rec.update({'payment_lines': lines})


class PosPaymentLine(models.Model):
    _name = 'pos.payment.line'

    session_id = fields.Many2one('pos.session', string="Session", ondelete='cascade')
    payment_method = fields.Char(string="Payment Method")
    amount = fields.Float(string="Amount")
