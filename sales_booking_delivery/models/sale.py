# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    rider_id = fields.Many2one("res.users", string="Delivery Rider", copy=False)

    def action_invoice_paid(self):
        res = super(AccountMove, self).action_invoice_paid()
        sale_ids = self.env['sale.order'].search([('delivery_status', '=', 'delivered')])
        for invoice in self:
            rider = self.env['res.rider'].search([('user_id', '=', invoice.rider_id.id), ('availability_type', '=', 'busy')])
            for sale in sale_ids:
                if invoice.id in sale.invoice_ids.ids:
                    self.env['sale.delivery.rider'].search([('order_id', '=', sale.id)]).write({'state': 'paid'})
                    sale.write({'delivery_status': 'paid'})
            rider.update_rider_status()
        return res

class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        self.ensure_one()
        if self.move_lines.mapped('origin_returned_move_id') and self.picking_type_code == 'incoming':
            sale_order = self.move_lines.mapped('sale_line_id.order_id')
            delivery_control = self.env['sale.delivery.rider'].search([('order_id', '=', sale_order.id)])
            self.env['res.rider'].search([('user_id', '=', delivery_control.res_id.id)]).write({'availability_type': 'free'})
        return super(Picking, self).button_validate()

    def action_done(self):
        res = super(Picking, self).action_done()
        move_lines = self.env['account.move.line']
        for pick in self.filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.sale_id and x.company_id.delivery_control):
            invoice_id = pick.sale_id._create_invoices()
            invoice_id.write({'rider_id': pick.sale_id.res_id.id})
            invoice_id.action_post()
            if pick.sale_id.invoice_ids and pick.sale_id.sale_payment_ids.filtered(lambda x: x.state == 'posted' and x.payment_type == 'inbound'):
                invoice_move = pick.sale_id.invoice_ids.mapped('line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                payment_move = pick.sale_id.sale_payment_ids.mapped('move_line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
                move_lines |= (invoice_move + payment_move) 
                move_lines.auto_reconcile_lines()
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_control = fields.Boolean(related='company_id.delivery_control')
    delivery_status = fields.Selection([
        ('draft', 'Processing'),
        ('ready', 'Ready'),
        ('assigned', 'Assigned'),
        ('delivered', 'Delivered'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], readonly=True, copy=False)
    is_online_shop = fields.Boolean(compute='_compute_is_online_shop')
    customer_mobile = fields.Char('Customer Mobile/Phone')
    commitment_date = fields.Datetime('Delivery Date',
                                      copy=False, readonly=False,
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.")
    delivered_time = fields.Datetime(compute='_compute_delivered_time')
    order_status = fields.Selection([('on_time', 'On Time'), ('late', 'Late')], compute='_compute_order_status')
    late_hours = fields.Char(string="Late Hours", compute="_compute_late_hours")

    def _compute_late_hours(self):
        for order in self:
            late = ''
            if order.order_status == 'late':
                late = order.delivered_time - order.commitment_date
            order.late_hours = late

    def _compute_order_status(self):
        for order in self:
            if order.delivered_time and (order.commitment_date <= order.delivered_time):
                order.order_status = 'late'
            elif order.delivered_time and (order.commitment_date > order.delivered_time):
                order.order_status = 'on_time'
            else:
                order.order_status = False

    def _compute_delivered_time(self):
        for order in self:
            dc = self.env['sale.delivery.rider'].search([('order_id', '=', order.id), ('delivered_time', '!=', False)], limit=1)
            order.delivered_time = dc.delivered_time

    @api.onchange('order_line')
    def onchange_order_line(self):
        if self.delivery_status and self.delivery_status not in ('draft', 'cancel'):
            raise UserError(_('Changes in Ready state are not allowed!'))

    @api.onchange('customer_mobile')
    def onchange_customer_mobile(self):
        partner = self.env['res.partner'].search(['|', ('mobile', '=', self.customer_mobile), ('phone', '=', self.customer_mobile)], limit=1)
        if partner and self.customer_mobile:
            self.partner_id = partner.id
        if not partner and self.customer_mobile:
            self.partner_id = self.env['res.partner'].sudo().create({
                'name': 'NEW',
                'phone': self.customer_mobile,
                'mobile': self.customer_mobile
            }).id

    def action_cancel(self):
        control_ids = self.env['sale.delivery.rider'].search([('order_id', '=', self.id)])
        if any(state in ('delivered', 'paid') for state in control_ids.mapped('state')):
            raise UserError(_('You cannot cancel this order!'))
        control_ids.write({'state': 'cancel'})
        self.env['res.rider'].search([('user_id', '=', self.res_id.id)]).update_rider_status()
        self.write({'delivery_status': 'cancel'})
        return super(SaleOrder, self).action_cancel()

    @api.constrains('commitment_date')
    def _check_commitment_date(self):
        for order in self:
            if order.commitment_date and order.commitment_date < fields.Datetime.now():
                raise UserError(_('Invalid delivery date !'))

    def _compute_is_online_shop(self):
        for order in self:
            order.is_online_shop = True if order.order_shop_id.channel_type == 'online' else False

    def action_sale_register_payment(self):
        sale_id = self.env.context.get('default_sale_id')
        if not sale_id:
            return ''

        return {
            'name': _('Register Payment'),
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('sales_booking_delivery.view_advance_payment_wizard').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def check_line_status(self):
        for order in self:
            if all(order.order_line.mapped('is_process')):
                order.new_line = False
            else:
                order.new_line = True
    
    def _compute_rider_count(self):
        for order in self:
            control_ids = self.env['sale.delivery.rider'].search([('order_id', '=', order.id)])
            order.rider_count = len(control_ids)

    order_shop_id = fields.Many2one(related='user_id.shop_id', store=True ,string="Order Shop")
    shop_id = fields.Many2one("pos.multi.shop", string="Pick-Up/Deliver Shop")
    channel_type = fields.Selection(related='order_shop_id.channel_type')
    order_type = fields.Selection([('pick_up', "Pick UP"), ('delivery', "Delivery")], string="Order Type")
    state = fields.Selection(selection_add=[('ready', 'Ready'), ('assign', 'Assigned'), ('delivered', 'Delivered')])
    res_id = fields.Many2one("res.users", string="Delivery Rider", copy=False)
    rider_count = fields.Integer('Rider Count', compute='_compute_rider_count')
    new_line = fields.Boolean(compute='check_line_status')

    @api.onchange('user_id')
    def onchange_order_shop(self):
        if self.user_id and self.user_id.shop_id:
            self.channel_type = self.user_id.shop_id.channel_type

    @api.onchange('shop_id')
    def onchange_order_shop(self):
        if self.shop_id and self.shop_id.warehouse_id:
            self.warehouse_id = self.shop_id.warehouse_id.id

    def action_assign(self):
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
            'context': {'default_rider_ids': [(4, x) for x in records.mapped('user_id').ids]},
            'target': 'new',
        }

    def action_create_deliver(self):
        for rec in self:
            ship_address = rec.partner_shipping_id and rec.partner_shipping_id.street or ''
            vals = {
                'partner_id': rec.partner_id.id or False,
                'order_id': rec.id or False,
                'del_address': ship_address,
                'channel_type': rec.channel_type,
                'order_type': rec.order_type, 
                'shop_id': rec.shop_id and rec.shop_id.id or False,
                'order_shop_id': rec.order_shop_id and rec.order_shop_id.id or False,
                'res_id': rec.res_id and rec.res_id.id or False,
                'street': rec.partner_id.street or '',
                'street2': rec.partner_id.street2 or '',
                'zip': rec.partner_id.zip or '',
                'commitment_date': rec.commitment_date,
                'city': rec.partner_id.city or '',
                'procession_time': fields.Datetime.now(),
                'state_id': rec.partner_id.state_id and rec.partner_id.state_id.id or False,
                'country_id': rec.partner_id.country_id and rec.partner_id.country_id.id or False,
            }
            rec.write({'delivery_status': 'draft'})
            self.env['sale.delivery.rider'].create(vals)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if not self.commitment_date and self.company_id.delivery_control:
            raise UserError(_('You need to set delivery date before confirm order!'))
        if self.company_id.delivery_control:
            self.action_create_deliver()
        return res
    
    def action_delivered(self):
        control_ids = self.env['sale.delivery.rider'].search([('order_id', '=', self.id)])
        if control_ids:
            control_ids.write({'state': 'delivered'})
        self.write({'state': 'delivered'})

    def action_ready(self):
        control_ids = self.env['sale.delivery.rider'].search([('order_id', '=', self.id)])
        if control_ids:
            control_ids.write({'state': 'ready'})
        self.write({'state': 'ready'})

    def action_view_rider(self):
        control_ids = self.env['sale.delivery.rider'].search([('order_id', '=', self.id)])
        return {
            'name': _('Delivery Control'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.delivery.rider',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', control_ids.ids)],
        }

    def action_view_request(self):
        control_ids = self.env['resupply.stock'].search([('sale_order_id', '=', self.id)])
        return {
            'name': _('Stock Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'resupply.stock',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', control_ids.ids)],
        }

    def action_stock_request(self):
        stock_request = self.env.ref('sales_booking_delivery.sale_stock_request_view_form', raise_if_not_found=False)
        return {
            'name': _('Create Stock Request'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.stock.request',
            'views': [(stock_request.id, 'form')],
            'view_id': stock_request.id,
            'context': {},
            'target': 'new',
        }

    def write(self, vals):
        if vals.get('commitment_date'):
            self.env['sale.delivery.rider'].search([('order_id', '=', self.id)]).write({'commitment_date': vals.get('commitment_date')})
            self.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel')).write({'scheduled_date': vals.get('commitment_date')})
        return super(SaleOrder, self).write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_process = fields.Boolean(string='Processed', copy=False)

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        # When modifying a one2many, _origin doesn't guarantee that its values will be the ones
        # in database. Hence, we need to explicitly read them from there.
        if self._origin:
            product_uom_qty_origin = self._origin.read(["product_uom_qty"])[0]["product_uom_qty"]
        else:
            product_uom_qty_origin = 0

        if self.state == 'sale' and self.product_id.type in ['product', 'consu'] and self.product_uom_qty < product_uom_qty_origin:
            # Do not display this warning if the new quantity is below the delivered
            # one; the `write` will raise an `UserError` anyway.
            if self.product_uom_qty < self.qty_delivered:
                return {}
            raise UserError(_('You are decreasing the ordered quantity! Do not forget to manually update the delivery order if needed.'))
        return {}


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_sub_type = fields.Selection([('kitchen', "Kitchen"), ('factory', "Factory"), ('other', "Other")], string="Order From", default='other')
