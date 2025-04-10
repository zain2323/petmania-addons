# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Midilaj (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api


class ProductBrand(models.Model):
    _inherit = 'product.template'

    # origin_id = fields.Many2one('product.origin', string='Origin')


# class BrandProduct(models.Model):
#     _name = 'product.origin'

#     name = fields.Char(String="Name")
#     brand_image = fields.Binary()
#     member_ids = fields.One2many('product.template', 'origin_id')
#     product_count = fields.Char(String='Product Count', compute='get_count_products', store=True)

#     @api.depends('member_ids')
#     def get_count_products(self):
#         self.product_count = len(self.member_ids)


class BrandPivot(models.Model):
    _inherit = 'sale.report'

    origin_id = fields.Many2one('product.origin', string='Origin')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['origin_id'] = ", t.origin_id as origin_id"
        groupby += ', t.origin_id'
        return super(BrandPivot, self)._query(with_clause, fields, groupby, from_clause)
