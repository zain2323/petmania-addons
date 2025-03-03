# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from datetime import timedelta, date


class DeliveryRider(models.Model):
    _name = "res.rider"
    _rec_name = "user_id"

    user_id = fields.Many2one('res.users', string="Delivery Rider")
    availability_type = fields.Selection([('free', "Free"), ('busy', "Busy")], string="Availability", default='free')
    shop_id = fields.Many2one("pos.multi.shop", string="Shop ID")

    def update_rider_status(self):
        import datetime
        from_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d') + ' 00:00:00'
        to_date = date.today().strftime('%Y-%m-%d') + ' 23:59:59'
        for rider in self.filtered(lambda x: x.availability_type == 'busy'):
            status = 'busy'
            all_delivery = self.env['sale.delivery.rider'].search([('res_id', '=', rider.user_id.id), ('create_date', '>=', from_date), ('create_date', '<=', to_date)])
            if all(cd.state in ('delivered', 'paid', 'cancel') for cd in all_delivery):
                status = 'free'
            rider.availability_type = status
