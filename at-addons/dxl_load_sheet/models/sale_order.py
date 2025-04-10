# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    load_sheet_id = fields.Many2one('load.sheet', copy=False)

    def generate_load_sheet(self):
        order_lines = self.mapped('order_line')
        product_ids = self.mapped('order_line.product_id')
        company_id = self.mapped('company_id')
        line_data = []
        for product in product_ids:
            quantity = sum(order_lines.filtered(lambda x: x.product_id.id == product.id).mapped('product_uom_qty'))
            line_data.append((0, 0, {
                'product_id': product.id,
                'quantity': quantity,
            }))
        load_sheet = self.env['load.sheet'].create({
            'name': 'NEW',
            'company_id': company_id.id,
            'load_sheet_lines': line_data,
            'sale_order_ids': self.ids,
        })
        self.write({'load_sheet_id': load_sheet.id})

    def open_wizard(self):
        if not self.env.user.has_group('dxl_load_sheet.group_load_sheet_user'):
            raise ValidationError(_('You have no access to generate load sheet.'))
        sale_order_ids = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        lc_sale_ids = sale_order_ids.filtered(lambda x: x.load_sheet_id)
        if lc_sale_ids:
            warning_msg = "<div class='alert alert-danger' role='alert'>The RFQ(s) <b>"+ ', '.join(lc_sale_ids.mapped('name')) + "</b> selected are already included in a previous load sheet. <br/>Do you want to generate a new load sheet for this RFQ ?</div>"""

            return {
                'name': 'Generate Load Sheet',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                "view_type": "form",
                'res_model': 'load.sheet.wizard',
                'target': 'new',
                'view_id': self.env.ref('dxl_load_sheet.load_sheet_wizard_view').id,
                'context': {
                    'active_id': self.id,
                    'default_sale_order_ids': self.env.context.get('active_ids'),
                    'default_warning_msg': warning_msg
                },
            }
        else:
            sale_order_ids.generate_load_sheet()
