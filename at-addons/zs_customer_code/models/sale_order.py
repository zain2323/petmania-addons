from odoo import api, fields, models, exceptions


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_code = fields.Integer(string="Customer Code", related='partner_id.id', store=True)

class SaleReportInherit(models.Model):
    _inherit = 'sale.report'

    customer_code = fields.Integer(string='Customer Code')
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['company_type'] = ", s.customer_code as customer_code"
        groupby += ', s.customer_code'
        res = super()._query(with_clause, fields, groupby, from_clause)
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_code = fields.Integer(string="Customer Code", related='partner_id.id', store=True)

    
class AccountInvoiceReport(models.Model):
    # , CASE WHEN line.product_id IS NOT NULL THEN sum(line.product_id.weight * line.product_uom_qty / u.factor * u2.factor) ELSE 0 END as weight
    _inherit = 'account.invoice.report'

    customer_code = fields.Integer(string='Customer Code')
    weight = fields.Float('Gross Weight', readonly=True)
    
    _depends = {
        'account.move': ['partner_id'],
    }

    def _select(self):
        res = super(AccountInvoiceReport,self)._select()
        select_str = res + """, move.customer_code as customer_code"""
        return select_str