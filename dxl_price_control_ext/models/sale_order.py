# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    readonly_price_unit = fields.Boolean(compute="_compute_readonly_price_unit")

    def _compute_readonly_price_unit(self):
        for line in self:
            line.readonly_price_unit = not self.env.user.has_group('dxl_price_control_ext.group_update_sales_price')

    @api.model
    def default_get(self,default_fields):
        res = super(SaleOrder, self).default_get(default_fields)
        res['readonly_price_unit'] = not self.env.user.has_group('dxl_price_control_ext.group_update_sales_price')
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    readonly_price_unit = fields.Boolean(compute="_compute_readonly_price_unit")

    def _compute_readonly_price_unit(self):
        for line in self:
            line.readonly_price_unit = not self.env.user.has_group('dxl_price_control_ext.group_update_invoice_price')

    @api.model
    def default_get(self,default_fields):
        res = super(AccountMove, self).default_get(default_fields)
        res['readonly_price_unit'] = not self.env.user.has_group('dxl_price_control_ext.group_update_invoice_price')
        return res
