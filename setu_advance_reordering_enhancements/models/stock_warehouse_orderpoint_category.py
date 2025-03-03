from odoo import api, fields, models, _
from datetime import datetime

class StockWarehouseOrderpointCategory(models.Model):
    _name = "stock.warehouse.orderpoint.category"
    _description= "Stock Reordering by Category"
    _rec_name = 'scm_grading_id'

    scm_grading_id = fields.Many2one("scm.grading", "Category", required=True)
    scheduler_date = fields.Datetime(required=True)
    # vendor_id = fields.Many2one('res.partner', help="Set the vendor to whom you want to place an order.")

    def run_category_scheduler(self):
        for x in self.search([('scheduler_date', '=', datetime.today().date())]):
            self._context.update({'custom_reordering_category_id': x.scm_grading_id.id})
            # if x.vendor_id:
            #     self._context.update({'custom_reordering_vendor_id': x.vendor_id})
            self.env['procurement.group'].run_scheduler()
