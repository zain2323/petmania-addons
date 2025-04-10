# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api


class ReorderingSlabQty(models.Model):
    _name = 'reordering.slab.qty'
    name = fields.Char()
    reordering_slab_lines = fields.One2many('reordering.slab.qty.lines','reordering_slab_id')

class ReorderingSlabQtyLines(models.Model):
    _name = 'reordering.slab.qty.lines'
    reordering_slab_id = fields.Many2one('reordering.slab.qty', ondelete="cascade")

    min_cost = fields.Float()
    max_cost = fields.Float()
    min_inventory = fields.Float()
    max_inventory = fields.Float()

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    reordering_slab = fields.Many2one('reordering.slab.qty')

    #
    # @api.onchange('reordering_slab')
    # def onchange_reordering_slab(self):
    #     if self._origin.ads_qty < 1 and self.product_min_qty == 0 and self.product_max_qty == 0 and self.reordering_slab.id and self._origin.product_id.standard_price > 0:
    #         line = self.reordering_slab.reordering_slab_lines.filtered(lambda r:self._origin.product_id.standard_price >= r.min_cost and self._origin.product_id.standard_price <= r.max_cost)
    #         product_min_qty = line.min_inventory
    #         product_max_qty = line.max_inventory
    #         if product_min_qty >  0 and product_max_qty > 0:
    #             self.product_min_qty = product_min_qty
    #             self.product_max_qty = product_max_qty

    def update_order_point_data(self):

        query = f"""update stock_warehouse_orderpoint as swo
              set product_min_qty =tmp.suggested_min_qty,
                  safety_stock = tmp.suggested_safety_stock,
                  product_max_qty = tmp.suggested_max_qty
              from(
                      select 	wo.id,
                               coalesce(wo.suggested_min_qty,0) AS suggested_min_qty,
                              coalesce(wo.suggested_safety_stock,0) AS suggested_safety_stock,
                              coalesce(wo.suggested_max_qty,0) AS suggested_max_qty
                      from stock_warehouse_orderpoint wo
                           join product_product prod on prod.id = wo.product_id
                      where prod.active = true
                            and prod.update_orderpoint = true
                            and wo.id in {tuple(self.ids) if len(self.ids) > 1 else '(' + str(self.id) + ')'}
              )tmp
              where swo.id = tmp.id"""
        self._cr.execute(query)

        if self.ads_qty < 1 and self.product_min_qty == 0 and self.product_max_qty == 0 and self.reordering_slab.id and self.product_id.standard_price > 0:
            line = self.reordering_slab.reordering_slab_lines.filtered(lambda r:self.product_id.standard_price >= r.min_cost and self.product_id.standard_price <= r.max_cost)
            product_min_qty = line.min_inventory
            product_max_qty = line.max_inventory
            if product_min_qty >  0 and product_max_qty > 0:
                self.product_min_qty = product_min_qty
                self.product_max_qty = product_max_qty
