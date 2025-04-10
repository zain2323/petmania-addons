from odoo import fields, models, api, _
from datetime import timedelta


class InventoryAnalysisReportLine(models.TransientModel):
    _name = 'inventory.analysis.report.product.line'
    _description = 'Inventory Analysis Report Product Lines'

    sequence = fields.Integer(string='Sequence')

    stage_line_ids = fields.One2many('inventory.analysis.report.stage.line', 'product_line_id')

    report_id = fields.Many2one('inventory.analysis.report')
    warehouse_line_ids = fields.One2many('inventory.analysis.report.warehouse.line', 'product_line_id')
    start_date = fields.Date(related='report_id.start_date')
    end_date = fields.Date(related='report_id.end_date')

    compute_totals = fields.Boolean(compute='_compute_compute_totals', store=True)
    total_ads = fields.Float(string='Total ADS')
    total_stock = fields.Float(string='Company Stock')
    totaL_total_sales = fields.Float(string='Total Sales')
    company_stamina = fields.Float(string='Company Stamina')

    product_id = fields.Many2one('product.product')
    name = fields.Char(related='product_id.display_name')


    @api.depends('warehouse_line_ids')
    def _compute_compute_totals(self):
        for rec in self:
            rec.total_stock = sum([i.onhand_quantity for i in rec.warehouse_line_ids])
            rec.total_ads = sum([i.avg_daily_sales for i in rec.warehouse_line_ids if (not i.warehouse_id.is_bonded)])
            rec.totaL_total_sales = sum([i.total_sales for i in rec.warehouse_line_ids])
            rec.company_stamina = rec.total_stock / rec.total_ads if rec.total_ads else False
            rec.compute_totals = True


    def _get_adsw(self, weight, ads):
        return weight * ads


    def _get_days_between_dates(self, start, end):
        date_difference = end-start
        if isinstance(date_difference, timedelta):
            return date_difference.days + 1
        else:
            return date_difference + 1