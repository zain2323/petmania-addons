from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    ntn = fields.Char('NTN')
    strn = fields.Char('STRN')


class ResCompany(models.Model):
    _inherit = 'res.company'

    ntn = fields.Char('NTN')
    strn = fields.Char('STRN')

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    ntn = fields.Char('NTN',related='company_id.ntn')
    strn = fields.Char('STRN',related='company_id.strn')
