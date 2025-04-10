from odoo import models, fields, api, _


class PurchaseOrderStage(models.Model):
    _name = 'purchase.order.stage'
    _description = 'Purchase Stage'
    _order = 'sequence asc, id asc'


    active = fields.Boolean(default=True)
    sequence = fields.Integer(string='Sequence', default=0, required=True)

    name = fields.Char('Name', required=True)
    
    stage_type = fields.Selection([
        ('direct', 'Direct'), ('indirect', 'Indirect')
    ], string='Type', default='direct', required=True)

    consignment_type = fields.Selection([
        ('normal', 'Normal'), ('bulk', 'Bulk')
    ], string='Imports', default='normal', required=True)

