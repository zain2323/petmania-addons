from odoo import models, fields, api
from odoo.exceptions import UserError

# access_recv_brand,recv.brand,model_recv_brand,,1,1,1,1

# class RecvBrand(models.Model):
#     _name = "recv.brand"

#     name = fields.Char(string='Brand Name')
   
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    recv_brand = fields.Many2one('product.brand', string="Recievable Brand", required=True)
    
    def _prepare_invoice(self):
        """
        This method would set the recv_brand during invoice creation.
        """
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        if self.recv_brand:
            invoice_vals.update({'recv_brand': self.recv_brand})
        return invoice_vals

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    recv_brand = fields.Many2one('product.brand', string="Recievable Brand", required=True)
    
class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    
    recv_brand = fields.Many2one('product.brand', string="Recievable Brand", related="sale_id.recv_brand")
    
class BrandReciveableReport(models.Model):
    _name = 'brand.recievable.report'
    _auto = False
    
    currency_id = fields.Many2one('res.currency', string="Currency",
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)
    recv_brand = fields.Many2one('product.brand', string="Recievable Brand")
    recievable = fields.Monetary('Recievable', help="Recievable of brand")
    # partner_ids = fields.Many2many('res.partner', string="Partners", compute="_compute_partner_ids", store=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    # product_id = fields.Many2one('product.product', string="Product")
    # def _compute_partner_ids(self):
    #     for rec in self:
    #         partners = []
    #         invoices = self.env['account.move'].search([('recv_brand', '=', rec.recv_brand)])
    #         for invoice in invoices:
    #             partners.append(invoice.partner_id)
    #         rec.partner_ids = [(6,0, partners)]
            
    def init(self):
        self._cr.execute(""" 
        CREATE OR REPLACE VIEW brand_recievable_report AS 
            WITH brands_table AS (
                SELECT id FROM product_brand
            )
            SELECT 
                row_number() OVER () as id,
                mv.recv_brand as recv_brand,
                SUM(mv.amount_residual) as recievable,
                mv.partner_id as partner_id
            FROM 
                account_move mv
            WHERE 
                mv.recv_brand IN (SELECT id FROM brands_table) AND
                mv.state = 'posted'
            GROUP BY 
                mv.recv_brand, mv.partner_id;
        """)
        # self._compute_partner_ids()
        

    
    