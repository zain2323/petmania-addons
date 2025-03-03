# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_brand_id'] = ", t.product_brand_id as product_brand_id"
        groupby += ', t.product_brand_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select_pos(self, fields=None):
        if not fields:
            fields = {}
        fields['product_brand_id'] = ', t.product_brand_id AS product_brand_id'
        return super()._select_pos(fields)

    def _group_by_pos(self):
        return super(SaleReport, self)._group_by_pos() + ',t.product_brand_id'


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _select(self):
        return super(PosOrderReport, self)._select() + ',pt.product_brand_id AS product_brand_id'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',pt.product_brand_id'
