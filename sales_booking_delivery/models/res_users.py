# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.osv.expression import get_unaccent_wrapper

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.constrains('groups_id')
    def _check_unique_shop(self):
        sale_group = self.env.ref('sales_booking_delivery.grp_booker') in self.groups_id or self.env.ref('sales_booking_delivery.grp_packing') in self.groups_id or self.env.ref('sales_booking_delivery.grp_supervisor') in self.groups_id
        if sale_group and not self.shop_id:
            raise UserError(_('Please assign shop in user !'))

    @api.depends('groups_id')
    def _compute_rider(self):
        for user in self:
            if self.env.ref('base.group_portal') in user.groups_id:
                user.is_deliver_rider = True
            else:
                user.is_deliver_rider = False

    is_deliver_rider = fields.Boolean(string='Is a Rider', compute='_compute_rider')
    deliver_rider = fields.Boolean(string='Delivery Rider', copy=False)
    shop_id = fields.Many2one("pos.multi.shop", string='Shop')
