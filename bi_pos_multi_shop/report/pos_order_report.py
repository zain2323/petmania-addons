# -*- coding: utf-8 -*-

from functools import partial

from odoo import models, fields


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    shop_id = fields.Many2one('pos.multi.shop', string='Shop', readonly=True)

    def _select(self):
        return super(PosOrderReport, self)._select() + ',s.shop_id AS shop_id'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',s.shop_id'
