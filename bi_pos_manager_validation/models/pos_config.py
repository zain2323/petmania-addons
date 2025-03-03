# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp

class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_security_pin = fields.Char(string='Security PIN', size=32, help='A Security PIN used to protect sensible functionality in the Point of Sale')

    @api.constrains('pos_security_pin')
    def _check_pin(self):
        if self.pos_security_pin and not self.pos_security_pin.isdigit():
            raise UserError(_("Security PIN can only contain digits"))



class PosConfigInherit(models.Model):
	_inherit = 'pos.config'

	user_id = fields.Many2one('res.users',string='Manager')
	close_pos = fields.Boolean(string='Closing Of POS')
	order_delete = fields.Boolean(string='Order Deletion')
	order_line_delete = fields.Boolean(string='Order Line Deletion')
	qty_detail = fields.Boolean(string='Add/Remove Quantity')
	discount_app = fields.Boolean(string='Apply Discount')
	payment_perm = fields.Boolean(string='Payment')
	price_change = fields.Boolean(string='Price Change')
	one_time_valid = fields.Boolean(string='One Time Password for an Order')
