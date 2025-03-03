# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosMultiShop(models.Model):
    _inherit = 'pos.multi.shop'

    @api.depends('deliver_rider_ids.shop_id')
    def _compute_users(self):
        user_ids = self.env['res.users'].search([('deliver_rider', '=', True)])
        print(user_ids,11111111111111111111)
        rider_ids = self.env['res.rider'].search([('user_id', 'in', user_ids.ids)])
        for rec in self:
            filter_ids = user_ids - rider_ids.mapped('user_id') - self.deliver_rider_ids.mapped('user_id')
            rec.user_ids = [(4, i.id) for i in filter_ids]

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', default=_default_warehouse_id)
    user_ids = fields.Many2many('res.users', string="Users", compute='_compute_users')
    channel_type = fields.Selection([('shop', "Shop"), ('call_center', "Call Center"), ('online', 'Online')], string="Channel")
    deliver_rider_ids = fields.One2many('res.rider', 'shop_id', string="Delivery Rider")
