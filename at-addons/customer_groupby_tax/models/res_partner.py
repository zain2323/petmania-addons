from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    tax_status = fields.Selection(string="Tax Status", 
            selection=[
            ("registered", "Registered"),
            ("non_registered", "Non Registered"),
            ("hybrid", "Hybrid")
            ])


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tax_status = fields.Selection(related='partner_id.tax_status',
                               string='Tax Status', store=True)

class SaleReport(models.Model):
    _inherit = 'sale.report'
    
    tax_status = fields.Selection(string="Tax Status", 
            selection=[
            ("registered", "Registered"),
            ("non_registered", "Non Registered"),
            ("hybrid", "Hybrid")
            ])
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['tax_status'] = ",s.tax_status"
        groupby += ',s.tax_status'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)    
    
class InvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    
    tax_status = fields.Selection(string="Tax Status", 
            selection=[
            ("registered", "Registered"),
            ("non_registered", "Non Registered"),
            ("hybrid", "Hybrid")
            ])
    
    _depends = {
        'account.move': ['partner_id', 'tax_status'],
        'res.partner': ['tax_status'],
    }

    def _select(self):
        return super()._select() + ", contact_partner.tax_status as tax_status, move.date"

    def _from(self):
        return super()._from() + " LEFT JOIN res_partner contact_partner ON contact_partner.id = move.partner_id"


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    tax_status = fields.Selection(related='partner_id.tax_status',
                               string='Tax Status', store=True)
    