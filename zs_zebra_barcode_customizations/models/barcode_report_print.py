# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, api, _
from reportlab.graphics import barcode
from base64 import b64encode


class TRReportBarcodeLabelsInherit(models.AbstractModel):
    _inherit = 'report.td_zebra_barcode_labels.report_product_tdzebrabarcode'

    @api.model
    def _get_lines(self, form):
        prod_obj = self.env['product.product']
        result = []
        dict_data = {}
        data_append = False
        price_display = form.get('price_display')
        barcode_font_size = form.get('barcode_font_size')
        currency_position = form.get('currency_position', 'before') or 'before'
        total_value = 0

        lines = form and form.get('product_ids', []) or []
        total_quantities = sum([int(x['qty']) for x in lines])
        user = self.env.user
        for l in lines:
            p = prod_obj.sudo().browse(l['product_id'])
            reordering_rule = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', p.id), ('company_id', '=', self.env.company.id)], limit=1)
            if reordering_rule:
                min_qty = reordering_rule.product_min_qty
                max_qty = reordering_rule.product_max_qty
            else:
                min_qty = 0
                max_qty = 0
            for c in range(0, int(l['qty'])):
                value = total_value % 2
                data_append = False
                symbol = self._get_symbol(p)
                if price_display:
                    price_value = str(round(p.lst_price, 2))
                    list_price = symbol + ' ' + price_value
                    if currency_position == 'after':
                        list_price = price_value + ' ' + symbol
                    dict_data.update({'list_price' + '_' + str(value): list_price})

                barcode_value = p[str(form['barcode_field'])]

                variant = ", ".join([v.name for v in p.product_template_attribute_value_ids])
                attribute_string = variant and "%s" % (variant) or ''
                dict_data.update({
                    'name' + '_' + str(value): p.name or '',
                    'min' + '_' + str(value): f"Min Qty: {min_qty}" or '',
                    'max' + '_' + str(value): f"Max Qty: {max_qty}" or '',
                    'code' + '_' + str(value): barcode_value,
                    'variants' + '_' + str(value): attribute_string or '',
                    'default_code' + '_' + str(value): p.default_code or '',
                    'barcode_font_size': barcode_font_size,
                })
                total_value += 1
                if total_value % 2 == 0:
                    result.append(dict_data)
                    data_append = True
                    dict_data = {}

        if not data_append:
            result.append(dict_data)
        return [x for x in result if x]
