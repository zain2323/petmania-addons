# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_apply_inventory(self):
        user = self.env.user.id
        for rec in self:
            if user not in rec.location_id.user_ids.ids:
                raise UserError("Sorry! You Have No Access For Current Destination location.")
        return super().action_apply_inventory()


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        user = self.env.user.id
        for rec in self:
            if user not in rec.location_dest_id.user_ids.ids or user not in rec.location_id.user_ids.ids:
                raise UserError("Sorry! You Have No Access For Current Destination location.")
        return super().button_validate()

class StockLocation(models.Model):
    _inherit = "stock.location"

    user_ids = fields.Many2many(comodel_name='res.users', relation='rel_stock_loc_ref_user_ref')

