from odoo import models, fields, api
from datetime import datetime, date, timedelta


class PurchaseStageHistory(models.Model):
    _name = 'purchase.stage.history'
    _description = 'Purchase Stage History'

    purchase_id = fields.Many2one('purchase.order')

    stage_id = fields.Many2one('purchase.order.stage', string='Stages')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    finished_date = fields.Date(string='Finished Date')

    delay_days = fields.Integer(string='Delay Days', compute='_compute_delay_days')

    @api.onchange('end_date', 'finished_date')
    def _compute_delay_days(self):
        for rec in self:
            if rec.end_date and rec.finished_date:
                difference = rec.finished_date - rec.end_date
                if isinstance(difference, timedelta):
                    rec.delay_days = difference.days if rec.finished_date > rec.end_date else -1*(abs(difference.days))
                else:
                    rec.delay_days = difference if rec.finished_date > rec.end_date else -1*(abs(difference))
            else:
                rec.delay_days = False
