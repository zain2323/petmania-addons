# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    customer_attributes = fields.Many2one('customer.attributes', string='Customer Attributes', readonly=True)


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['customer_attributes'] = ", s.customer_attributes as customer_attributes"
        groupby += ', s.customer_attributes'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)