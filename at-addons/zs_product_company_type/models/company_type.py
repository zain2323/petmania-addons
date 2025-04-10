from odoo import models, fields, api
from odoo.exceptions import UserError
    
class ProductCompanyType(models.Model):
    _name = "product.company.type"
    
    name = fields.Char(string="Name")
    

class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_type = fields.Many2one(
        "product.company.type", string="Company Type"
    )

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    
    custom_company_type = fields.Many2one('product.company.type', string='Company Type')
    
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    company_type = fields.Many2one(
        "product.company.type", string="Company Type"
    )

class SaleOrderInherit(models.Model):
    _inherit = "sale.order.line"

    company_type = fields.Many2one(related='product_id.company_type',
                               string='Company Type POS', store=True, readonly=True)



class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    company_type = fields.Many2one(related='product_id.company_type',
                               string='Company Type POS', store=True, readonly=True)

   
class SaleReportInherit(models.Model):
    _inherit = 'sale.report'

    company_type = fields.Many2one('product.company.type', string='Company Type')
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['company_type'] = ", l.company_type as company_type"
        groupby += ', l.company_type'
        res = super()._query(with_clause, fields, groupby, from_clause)
        return res

    def _select_pos(self, fields=None):
        fields['company_type'] = ', l.company_type as company_type'
        return super()._select_pos(fields)

    def _group_by_pos(self):
        res = super()._group_by_pos()
        res += ', l.company_type'
        return res
        

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    company_type = fields.Many2one(related='product_id.company_type',
                               string='Company Type', store=True, readonly=True)

class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    company_type = fields.Many2one('product.company.type', string='Company Type')
    
    _depends = {
        'account.move.line': ['product_id'],
    }

    def _select(self):
        res = super(AccountInvoiceReport,self)._select()
        select_str = res + """, line.company_type AS company_type"""
        return select_str

class ProductClassificationReportStock(models.Model):
    _inherit = 'stock.quant'

    company_type = fields.Many2one(related='product_id.product_tmpl_id.company_type',
                               string='Company Type', store=True, readonly=True)
    
class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"

    company_type = fields.Many2one(related='product_id.company_type',
                               string='Company Type', store=True, readonly=True)
    
class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    company_type = fields.Many2one('product.company.type', string='Company Type')
    
    def _select(self):
        return super(PurchaseReport, self)._select() + ", t.company_type as company_type"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", t.company_type"
    

class ProductCategoryInherit(models.Model):
    _inherit = "product.category"
    
    company_type = fields.Many2one('product.company.type', string='Company Type')
    

class StockValuation(models.Model):
    _inherit = "stock.valuation.layer"
    
    company_type = fields.Many2one(related='product_tmpl_id.company_type',
                               string='Company Type', store=True, readonly=True)

class ProductBrandInherit(models.Model):
    _inherit = "product.brand"
    
    company_type = fields.Many2one('product.company.type', string='Company Type')