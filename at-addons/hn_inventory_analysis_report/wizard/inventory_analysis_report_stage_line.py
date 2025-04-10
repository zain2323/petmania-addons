from odoo import fields, models, api, _


class InventoryAnalysisStageLine(models.TransientModel):
    _name = 'inventory.analysis.report.stage.line'
    _description = 'Inventory Analysis Report Stage Lines'

    product_line_id = fields.Many2one('inventory.analysis.report.product.line')
    stage_id = fields.Many2one('purchase.order.stage')
    quantity = fields.Float(string='Quantity')