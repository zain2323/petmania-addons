# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AdvancePaymentWizard(models.TransientModel):
    _name = 'advance.payment.wizard'

    partner_id = fields.Many2one('res.partner')
    sale_id = fields.Many2one('sale.order')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(required=True)
    journal_id = fields.Many2one('account.journal')

    @api.model
    def default_get(self, fields):
        res = super(AdvancePaymentWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        sale = self.env['sale.order'].browse(active_id)
        res.update({
            'sale_id': active_id,
            'partner_id': sale.partner_id.id,
        })
        return res

    def create_advance_payment(self):
        # exchange_rate = self.env['res.currency']._get_conversion_rate(invoice.company_id.currency_id, invoice.currency_id, invoice.company_id, invoice.invoice_date)
        # currency_amount = amount * (1.0 / exchange_rate)
        payment_dict = {
            'payment_type': 'inbound',
            'partner_id': self.partner_id.id,
            'partner_type': 'customer',
            'journal_id': self.journal_id.id,
            'company_id': self.journal_id.company_id.id,
            # 'currency_id':self.journal_id.currency_id.id,
            'payment_date': fields.Date.today(),
            'amount': abs(self.amount),
            'name': _("Payment") + " - " + self.sale_id.name,
            'communication': self.sale_id.name,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id
        }
        payment = self.env['account.payment'].create(payment_dict)
        payment.sudo().post()


class DeliverRiderLine(models.TransientModel):
    _name = "deliver.rider.wizard.line"

    dev_rider_id = fields.Many2one('deliver.rider.wizard', string="Riders")
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    state = fields.Char('State')

class DeliverRider(models.TransientModel):
    _name = "deliver.rider.wizard"

    rider_ids  = fields.Many2many('res.users', string='Free Rider')
    user_id = fields.Many2one('res.users', string="Select Rider")
    assign_type = fields.Selection([('sale', "Sale"), ('delivery', "Delivery")], string="Type", default='delivery')
    rider_line_ids = fields.One2many('deliver.rider.wizard.line', 'dev_rider_id', 'Deliveries') 

    @api.model
    def _prepare_rider_lines(self, line):
        return {
            'sale_id': line.order_id.id,
            'state': line.state,
        }

    @api.model
    def default_get(self, fields_list):
        lines = []
        res = super(DeliverRider, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            deliveries = self.env['sale.delivery.rider'].browse(active_ids).filtered(lambda x: x.state == 'ready' and x.order_type == 'delivery')
            print(deliveries,111111111111)
            del_riders = deliveries.mapped('shop_id').mapped('deliver_rider_ids')
            print(del_riders,22222222222)
            riders = del_riders.filtered(lambda x: x.availability_type == 'free')
            for deliver in deliveries:
                lines.append((0, 0, self._prepare_rider_lines(deliver)))
            res['rider_line_ids'] = lines
            res['rider_ids'] = riders.mapped('user_id').ids
        return res

    def add_deliver(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            delivery_ids = self.env['sale.delivery.rider'].browse(active_ids).filtered(lambda x: x.state == 'ready' and x.order_type == 'delivery')
            if delivery_ids and self.user_id:
                delivery_ids.mapped('order_id').write({'res_id': self.user_id.id, 'delivery_status': 'assigned'})
                delivery_ids.write({'res_id': self.user_id.id, 'state': 'assign', 'assinged_time': fields.Datetime.now()})
            rider_ids = delivery_ids.mapped('shop_id').mapped('deliver_rider_ids')
            if rider_ids and self.user_id:
                lines = rider_ids.filtered(lambda x: x.user_id and x.user_id == self.user_id)
                if lines:
                    lines.write({'availability_type': 'busy'})
        return True

class SaleStockRequest(models.TransientModel):
    _name = "sale.stock.request"

    sale_request_ids = fields.One2many('sale.stock.request.line', 'sale_request_id', string="Riders")
    set_all = fields.Boolean(string="Select All")

    @api.onchange('set_all')
    def onchange_set_all(self):
        if self.set_all:
            self.mapped('sale_request_ids').write({'final_check': True})
        else:
            self.mapped('sale_request_ids').write({'final_check': False})

    @api.model
    def _prepare_request_lines(self, line, sequence):
        return {
            'sequence': sequence,
            'sale_order_id': line.order_id.id,
            'sale_line_id': line.id,
            'product_id': line.product_id.id,
            'barcode' : line.product_id.barcode,
            'qty': line.product_uom_qty,
            'uom_id': line.product_uom.id,
            'requisition_date': line.order_id.commitment_date,
        }

    @api.model
    def default_get(self, fields_list):
        lines = []
        sequence = 0
        res = super(SaleStockRequest, self).default_get(fields_list)
        active_id = self.env.context.get('active_model') == 'sale.order' and self.env.context.get('active_id')
        if active_id:
            order_id = self.env['sale.order'].search([('id', '=', active_id)], limit=1)
            sale_line_ids = order_id.mapped('order_line').filtered(lambda x: x.product_id.product_sub_type == 'factory' and not x.is_process)
            for line in sale_line_ids:
                sequence = sequence + len(line)
                lines.append((0, 0, self._prepare_request_lines(line, sequence)))
            res['sale_request_ids'] = lines
        return res

    def _request_lines(self, line):
        return {
            'stock': line.product_id.id,
            'description': line.product_id.display_name,
            'on_hand_qty': line.product_id.qty_available,
            'qty': line.qty,
            'expected_date': line.requisition_date,
            'remarks': line.remark,
        }

    def create_stock_request(self):
        location = self.env['stock.location'].search([('usage', '=', 'internal'), ('is_factory', '=', True)], limit=1)
        if not location:
            raise ValidationError(_('Location for factory not found !'))
        request_ids = self.sale_request_ids.filtered(lambda x: x.final_check)
        if self.sale_request_ids.filtered(lambda x: not x.remark):
            raise ValidationError(_('Please enter remark !'))
        department_ids = request_ids.mapped('product_id').mapped('department_id')
        order_id = request_ids.mapped('sale_order_id')
        if order_id:
            for depart in department_ids:
                req_lines = []
                for line in request_ids.filtered(lambda x: x.product_id.department_id == depart):
                    req_lines.append((0, 0, self._request_lines(line)))
                    if line.final_check:
                        line.sale_line_id.is_process = True
                self.env['resupply.stock'].create({
                    'int_loc': depart.factory_id.id,
                    'dest_loc': order_id.shop_id.stock_location_id and order_id.shop_id.stock_location_id.id or False,
                    'department_id': depart.id,
                    'sale_order_id' : order_id and order_id.id,
                    'request_date': order_id.commitment_date,
                    'product_line': req_lines,
                    'state': 'in_progress',
                })
        return True

class SaleStockRequestLine(models.TransientModel):
    _name = "sale.stock.request.line"

    sequence = fields.Integer('SN')
    sale_request_id = fields.Many2one('sale.stock.request',string='Stock Request')
    requisition_date = fields.Datetime(default=fields.Datetime.now(), string='Date')
    sale_order_id = fields.Many2one('sale.order',string='Order #')
    sale_line_id = fields.Many2one('sale.order.line',string='Sale Lines')
    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('uom.uom',string='Unit')
    qty = fields.Float('Qty')
    barcode = fields.Char(string='Barcode')
    remark = fields.Char(string='Remark', required=True)
    final_check = fields.Boolean(string='Check')

    @api.onchange('qty')
    def onchnage_qty(self):
        for line in self.filtered(lambda x: x.qty and x.sale_line_id):
            if line.qty > line.sale_line_id.product_uom_qty:
                raise ValidationError(_('You can not assign more then ordered qty !'))