from odoo import models, fields, api

class ProductClassification(models.Model):
    _name = "product.classification"
    
    name = fields.Char(string="Name")
    
class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_classfication_id = fields.Many2one(
        "product.classification", string="Product Classification"
    )

class ProductProduct(models.Model):
    _inherit = "product.product"

    product_classfication_id = fields.Many2one(
        "product.classification", string="Product Classification"
    )

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    product_classfication_id = fields.Many2one(
        "product.classification", string="Product Classification"
    )

class SaleReportInherit(models.Model):
    _inherit = 'sale.report'

    product_classfication_id = fields.Many2one('product.classification', string='Product Classification')
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_classfication_id'] = ", t.product_classfication_id as product_classfication_id"
        groupby += ', t.product_classfication_id'
        return super(SaleReportInherit, self)._query(with_clause, fields, groupby, from_clause)


# class AccountMove(models.Model):
#     _inherit = 'account.move'
    
#     product_classfication_id = fields.Many2one('product.classification', string='Product Classification')
    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    product_classfication_id = fields.Many2one(related='product_id.product_classfication_id',
                               string='Product Classification', store=True, readonly=True)

    
class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    product_classfication_id = fields.Many2one('product.classification', string='Product Classification')
    
    _depends = {
        'account.move.line': ['product_id'],
    }

    def _select(self):
        res = super(AccountInvoiceReport,self)._select()
        select_str = res + """, line.product_classfication_id AS product_classfication_id """
        return select_str

class ProductClassificationReportStock(models.Model):
    _inherit = 'stock.quant'

    product_classfication_id = fields.Many2one(related='product_id.product_classfication_id',
                               string='Product Classification', store=True, readonly=True)

