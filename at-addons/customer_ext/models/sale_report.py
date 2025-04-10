# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    order_booker_id = fields.Many2one('customer.order.booker', string="Sponsor Captain", readonly=True)
    backup_captain = fields.Many2one('customer.order.booker', string="Backup Captain", readonly=True)
    type_id = fields.Many2one('customer.type', string='Customer Type', readonly=True)

    # def _select_sale(self, fields=None):
    #     res = super()._select_sale(fields)
    #     # res += ", s.order_booker_id as order_booker_id"
    #     res += ", e.type_id as type_id"
    #     return res

    # def _group_by_sale(self, groupby=''):
    #     res = super()._group_by_sale(groupby)
    #     res += ", e.type_id"
    #     return res

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['type_id'] = ", s.type_id as type_id"
        fields['order_booker_id'] = ", s.order_booker_id as order_booker_id"
        fields['backup_captain'] = ", s.backup_captain as backup_captain"
        groupby += ', s.type_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

