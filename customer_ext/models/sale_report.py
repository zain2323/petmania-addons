# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    order_booker_id = fields.Many2one('customer.order.booker', string="Order Booker")
    type_id = fields.Many2one('customer.type', string='Customer Type')

    def _select_sale(self, fields=None):
        res = super()._select_sale(fields)
        res += ", s.order_booker_id as order_booker_id"
        res += ", s.type_id as type_id"
        return res

    def _group_by_sale(self, groupby=''):
        res = super()._group_by_sale(groupby)
        res += ", s.order_booker_id"
        res += ", s.type_id"
        return res
