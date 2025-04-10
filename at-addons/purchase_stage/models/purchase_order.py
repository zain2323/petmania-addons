from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import math


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    stage_id = fields.Many2one('purchase.order.stage', string='Stages', tracking=True,
                                domain="[('stage_type','=',stage_type), ('consignment_type','=',consignment_type)]")

    stage_type = fields.Selection([
        ('direct', 'Direct'), ('indirect', 'Indirect')
    ], string='Type', default='direct', required=True)

    consignment_type = fields.Selection([
        ('normal', 'Normal'), ('bulk', 'Bulk')
    ], string='Imports', default='normal', required=True)

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    finished_date = fields.Date(string='Finished Date')
    delay_days = fields.Integer(string='Delay Days', compute='_compute_delay_days')

    stage_history_ids = fields.One2many('purchase.stage.history', 'purchase_id', readonly=True)


    # @api.constrains('start_date', 'end_date')
    # def _constrains_start_end_dates(self):
    #     for rec in self:
    #         if rec.start_date and rec.end_date:
    #             if rec.stage_id and rec.start_date > rec.end_date:
    #                 raise ValidationError('End Date should always be greater than Start Date')
    

    @api.constrains('stage_id')
    def _constrains_stage_id(self):
        for rec in self:
            if not rec.id:
                continue
            self.env.cr.execute(f"""
                SELECT
                    stage.sequence AS sequence,
                    stage.id AS id
                FROM purchase_order po
                JOIN purchase_order_stage stage ON po.stage_id=stage.id
                WHERE po.id={rec.id}
            """)
            res = self.env.cr.dictfetchone() or {}
            old_seq, old_id = res.get('sequence', 0), res.get('id', 0)
            
            if old_id == 0:
                continue

            if old_seq > rec.stage_id.sequence or (old_seq == rec.stage_id.sequence and old_id>rec.stage_id.id):
                raise ValidationError('Going back in stage is not allowed')
                    


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


    def _update_start_end_dates(self):
        self.ensure_one()

        if not (self.stage_id and self.partner_id):
            return
        
        self.env.cr.execute( f"""
            SELECT AVG(hist.end_date - hist.start_date) AS avg_diff
            FROM purchase_stage_history hist
            JOIN purchase_order po ON po.id=hist.purchase_id
            WHERE po.partner_id={self.partner_id.id} AND hist.stage_id={self.stage_id.id}
        """)
        avg_diff = self.env.cr.dictfetchone()['avg_diff']
        
        if not self.start_date:
            start_date = self.stage_history_ids.sorted(lambda x: x.id)[-1].finished_date if self.stage_history_ids else date.today()
            end_date = start_date + timedelta(days=math.ceil(avg_diff)) if avg_diff else False
            self.write({
                'start_date' : start_date, 
                'end_date' : end_date
            })
        else:
            self.end_date = self.start_date + timedelta(days=math.ceil(avg_diff)) if avg_diff else False
            

    def write(self, vals):
        
        # if stage is changed, maintain the history of previous stage
        is_new_stage = vals.get('stage_id', False)
        check_date = vals.get('start_date') or vals.get('end_date')

        for rec in self:

            # maintain history of previous stage
            if not (is_new_stage and rec.stage_id):
                continue

            # check if start date, end date and finished dates are entered 
            if not ((rec.start_date or vals.get('start_date')) and (rec.end_date or vals.get('end_date')) and
                    (rec.finished_date or vals.get('finished_date'))):
                raise ValidationError('Please Enter Start, End and Finished Dates')
                
            # create history
            hist = self.env['purchase.stage.history'].create({
                'purchase_id' : rec.id,
                'stage_id' : rec.stage_id.id,
                'start_date' : vals.get('start_date') or rec.start_date,
                'end_date' : vals.get('end_date') or rec.end_date,
                'finished_date' : vals.get('finished_date') or rec.finished_date
            })
        
        if is_new_stage:
            vals.update({
                'start_date' : False,
                'end_date' : False,
                'finished_date' : False
            })
        response = super().write(vals)

        for rec in self:
            # start and end date constrains
            if check_date:
                if rec.start_date and rec.end_date and rec.stage_id and rec.start_date > rec.end_date:
                    raise ValidationError('End Date should always be greater than Start Date')
            # after maintaining the history, update start, end and finshed dates
            if not rec.start_date or vals.get('stage_id') or vals.get('partner_id') or vals.get('start_date'):
                rec._update_start_end_dates()
            
            # update stage to first stage if rfq is sent
            if vals.get('state') == 'sent':
                stage_domain = [('stage_type','=',rec.stage_type), ('consignment_type','=',rec.consignment_type)]
                rec.stage_id = self.env['purchase.order.stage'].search(stage_domain, order='sequence asc, id asc', limit=1).id
        
        return response
        
    
    def _cron_create_activity(self, user_ids):
        purchases = self.env['purchase.order'].search([('end_date', '=', date.today())])
        for po in purchases:

            for user in user_ids:
                po.activity_schedule(
                    activity_type_id = self.env.ref('mail.mail_activity_data_todo').id,
                    summary = 'Purchase Order Stage Review',
                    note='Purchase Order Stage\'s end date is here, please update the status or increase the end date',
                    date_deadline = date.today(),
                    user_id = user
                )
    

    def button_confirm(self):
        response = super().button_confirm()

        for rec in self:
            stage_domain = [('stage_type','=',rec.stage_type), ('consignment_type','=',rec.consignment_type),
                            ('sequence','>=',rec.stage_id.sequence), ('id','>',rec.stage_id.id)]
            stage = self.env['purchase.order.stage'].search(stage_domain, order='sequence asc, id asc', limit=1)
            if stage:
                rec.stage_id = stage.id
        
        return response