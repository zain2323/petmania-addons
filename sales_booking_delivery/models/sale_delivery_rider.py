# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleDeliveryRider(models.Model):
    _name = "sale.delivery.rider"
    _rec_name = "order_id"

    partner_id = fields.Many2one('res.partner', string="Customer")
    shop_id = fields.Many2one("pos.multi.shop", string="Order Shop")
    order_shop_id = fields.Many2one('pos.multi.shop', string="Pick-Up/Deliver Shop")
    channel_type = fields.Selection([('shop', "Shop"), ('call_center', "Call Center"), ('online', 'Online')], string="Channel")
    order_type = fields.Selection([('pick_up', "Pick UP"), ('delivery', "Delivery")], string="Order Type")
    order_id = fields.Many2one('sale.order', string="Order")
    state = fields.Selection([('draft', 'Processing'), ('ready', 'Ready'), ('assign', 'Assigned'), ('delivered', 'Delivered'), ('paid', 'Paid'), ('cancel', 'Cancelled')], string="State", default='draft')
    res_id = fields.Many2one("res.users", string="Delivery Rider")
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    del_address = fields.Char('Address')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    procession_time = fields.Datetime('Processing Time', readonly=True)
    ready_time = fields.Datetime('Ready Time', readonly=True)
    assinged_time = fields.Datetime('Assigned Time', readonly=True)
    delivered_time = fields.Datetime('Delivered Time', readonly=True)
    delivery_visible = fields.Boolean(compute='_delivery_visible')
    commitment_date = fields.Datetime('Delivery Date', readonly=True)

    def action_open_delivery_control(self):
        return {
            'name': 'Delivery Control',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('shop_id', '=', self.env.user.shop_id.id)],
            'res_model': 'sale.delivery.rider',
            'target': 'current'
        }

    def _delivery_visible(self):
        is_supervisor = self.env.user.has_group('sales_booking_delivery.grp_booker')
        for delivery in self:
            if (is_supervisor and delivery.res_id and delivery.state == 'assign' and delivery.order_type == 'delivery') or (is_supervisor and delivery.order_type == 'pick_up' and delivery.state == 'ready'):
                delivery.delivery_visible = True
            else:
                delivery.delivery_visible = False

    @api.onchange('state_id')
    def onchange_state_id(self):
        for record in self:
            if record.state_id:
                record.country_id = record.state_id.country_id or False
            else:
                record.country_id = False

    @api.onchange('country_id')
    def onchange_cont_id(self):
        state_ids = []
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    def action_ready(self):
        if self.order_id:
            self.order_id.write({'delivery_status': 'ready'})
        self.write({'state': 'ready', 'ready_time': fields.Datetime.now()})


    def action_assign(self):
        if self.order_id:
            records = self.shop_id.mapped('deliver_rider_ids').filtered(lambda x: x.availability_type == 'free')
            deliver_rider = self.env.ref('sales_booking_delivery.deliver_rider_view_form', raise_if_not_found=False)
            return {
                'name': _('Assign Delivery Rider'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'deliver.rider.wizard',
                'views': [(deliver_rider.id, 'form')],
                'view_id': deliver_rider.id,
                'context': {'default_rider_ids': [(4, x) for x in records.mapped('user_id').ids], 'default_assign_type': 'delivery'},
                'target': 'new',
            }
  
    def action_delivered(self):
        if self.order_id:
            for picking in self.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel')):
                for move in picking.move_lines:
                    move.write({'quantity_done': move.product_uom_qty})
                picking.button_validate()

            #  Incase of sale order has only service product
            if not self.order_id.picking_ids:
                move_lines = self.env['account.move.line']
                invoice = self.order_id._create_invoices()
                invoice.write({'rider_id': self.order_id.res_id.id})
                invoice.action_post()
                if invoice and self.order_id.sale_payment_ids.filtered(lambda x: x.state == 'posted' and x.payment_type == 'inbound'):
                    invoice_move = self.order_id.invoice_ids.mapped('line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                    payment_move = self.order_id.sale_payment_ids.mapped('move_line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                    move_lines |= (invoice_move + payment_move) 
                    move_lines.auto_reconcile_lines()

        state = 'delivered'
        if self.order_id.invoice_ids and self.order_id.invoice_ids[0].amount_residual == 0:
            state = 'paid'
        self.write({'delivered_time': fields.Datetime.now(), 'state': state})
        rider = self.env['res.rider'].search([('user_id', '=', self.res_id.id), ('availability_type', '=', 'busy')])
        rider.update_rider_status()
        self.order_id.write({'delivery_status': state})

    def unlink(self):
        if any(rider.state != 'draft' for rider in self):
            raise ValidationError(_("You can only delete draft deliver control"))
        return super(SaleDeliveryRider, self).unlink()
