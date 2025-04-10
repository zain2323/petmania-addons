# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _

class StockBypassCompany(models.TransientModel):
    _name = "stock.bypass.company"
    _description = "Stock Bypass Company"
    _rec_name = 'name'

    name = fields.Char(default="Multi Company Products")
    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company')
    location_id = fields.Many2one('stock.location')
    inventory_quantity_auto_apply = fields.Float(string="On hand Quantity")
    available_quantity = fields.Float(string="Available Quantity")
    reordering_min_qty = fields.Float(string="Min")
    reordering_max_qty = fields.Float(string="Max")


    def get_data(self):
        data = []
        # product_variant_id
        existing = self.sudo().search([])
        existing.sudo().unlink()
        for stock in self.env['stock.quant'].sudo().search([('location_id.usage','=', 'internal')]):
            data.append({
                'product_id': stock.product_id.id,
                'company_id': stock.company_id.id,
                'location_id': stock.location_id.id,
                'inventory_quantity_auto_apply': stock.inventory_quantity_auto_apply,
                'available_quantity': stock.available_quantity,
                'reordering_min_qty': stock.product_id.product_tmpl_id.reordering_min_qty,
                'reordering_max_qty': stock.product_id.product_tmpl_id.reordering_max_qty,
            })
        datas = self.sudo().create(data)
        return {
            'name': _('Products'),
            'res_model': 'stock.bypass.company',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('find_product.view_stock_bypass_company_tree').id,
            'target': 'current',
            'context': {},
            'domain': [('id', 'in', datas.ids)],
            'xml_id': self.env.ref('find_product.view_stock_bypass_company_action2').id,
        }

    def _compute_nbr_reordering_rules(self):
        read_group_res = self.env['stock.warehouse.orderpoint'].read_group(
            [('product_id', 'in', self.ids)],
            ['product_id', 'product_min_qty', 'product_max_qty'],
            ['product_id'])
        res = {i: {} for i in self.ids}
        for data in read_group_res:
            res[data['product_id'][0]]['nbr_reordering_rules'] = int(data['product_id_count'])
            res[data['product_id'][0]]['reordering_min_qty'] = data['product_min_qty']
            res[data['product_id'][0]]['reordering_max_qty'] = data['product_max_qty']
        for product in self:
            product_res = res.get(product.id) or {}
            product.nbr_reordering_rules = product_res.get('nbr_reordering_rules', 0)
            product.reordering_min_qty = product_res.get('reordering_min_qty', 0)
            product.reordering_max_qty = product_res.get('reordering_max_qty', 0)
