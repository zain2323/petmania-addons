from odoo import models, fields, api

    
class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    product_weight = fields.Float(related='product_id.weight',
                               string='Weight', store=True, readonly=True)
   
class SaleReportInherit(models.Model):
    _inherit = 'sale.report'

    product_weight = fields.Float(string='Product Weight')
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_weight'] = ", l.product_weight as product_weight"
        groupby += ', l.product_weight'
        return super(SaleReportInherit, self)._query(with_clause, fields, groupby, from_clause)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_weight = fields.Float(related='product_id.weight',
                               string='Product Weight', store=True, readonly=True)

class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    product_weight = fields.Float(string='Product Weight')
    weight = fields.Float('Gross Weight', readonly=True)

    _depends = {
        'account.move.line': ['product_id'],
        'account.move': ['partner_id']
    }

    def _select(self):
        res = super(AccountInvoiceReport,self)._select()
        select_str = res + """, line.product_weight as product_weight, CASE WHEN line.product_id IS NOT NULL THEN (product.weight * line.quantity / uom_line.factor * uom_template.factor) ELSE 0 END as weight"""
        return select_str

class ProductClassificationReportStock(models.Model):
    _inherit = 'stock.quant'

    product_weight = fields.Float(related='product_id.weight',
                               string='Product Weight', store=True, readonly=True)

class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"

    product_weight = fields.Float(related='product_id.weight',
                               string='Product Weight', store=True, readonly=True)

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    product_weight = fields.Float(string='Product Weight')

    def _select(self):
        return super(PurchaseReport, self)._select() + ", l.product_weight"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", l.product_weight"   