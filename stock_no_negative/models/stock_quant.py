# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from collections import deque
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        result = super(StockQuant, self)._update_reserved_quantity(product_id, location_id, quantity, lot_id, package_id, owner_id, strict)
        quants = self.env['stock.quant'].sudo()
        for quant, qty in result:
            quants |= quant
        if quants:
            self.env['stock.update'].broadcast(quants)
        return result

    @api.model
    def get_qty_available(self, picking_type_id, product_ids=None):
        if picking_type_id:
            domain = [('id', '=', picking_type_id)]
            picking_type = self.env['stock.picking.type'].search(domain, limit=1)
            location_id = picking_type and picking_type.default_location_src_id.id
            domain = [
                ('usage', '=', 'internal'),
                ('id', 'child_of', location_id)
            ]
            all_locations = self.env['stock.location'].search(domain)
            quant_domain = [('location_id', 'in', all_locations.ids)]
            if product_ids:
                quant_domain.append(('product_id', 'in', product_ids))
            stock_quant = self.search_read(quant_domain,
                ['product_id', 'available_quantity', 'location_id'])
            return stock_quant

    @api.model
    def create(self, vals):
        res = super(StockQuant, self).create(vals)
        if res.location_id.usage == 'internal':
            self.env['stock.update'].broadcast(res)
        return res

    # def write(self, vals):
    #     record = self.filtered(lambda x: x.location_id.usage == 'internal')
    #     res = super(StockQuant, self).write(vals)
    #     self.env['stock.update'].broadcast(record)
    #     return res

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        check_negative_qty = (
            config["test_enable"] and self.env.context.get("test_stock_no_negative")
        ) or not config["test_enable"]
        if self.env.context.get("from_pos"):
            return
        if not check_negative_qty:
            return

        for quant in self:
            disallowed_by_product = (
                not quant.product_id.allow_negative_stock
                and not quant.product_id.categ_id.allow_negative_stock
            )
            disallowed_by_location = not quant.location_id.allow_negative_stock
            if (
                float_compare(quant.quantity, 0, precision_digits=p) == -1
                and quant.product_id.type == "product"
                and quant.location_id.usage in ["internal", "transit"]
                and disallowed_by_product
                and disallowed_by_location
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.name_get()[0][1]
                raise ValidationError(
                    _(
                        "You cannot validate this stock operation because the "
                        "stock level of the product '%(name)s'%(name_lot)s would "
                        "become negative "
                        "(%(q_quantity)s) on the stock location '%(complete_name)s' "
                        "and negative stock is "
                        "not allowed for this product and/or location."
                    )
                    % {
                        "name": quant.product_id.display_name,
                        "name_lot": msg_add,
                        "q_quantity": quant.quantity,
                        "complete_name": quant.location_id.complete_name,
                    }
                )

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        from_pos = False
        if 'POS' in self.mapped('picking_type_id.sequence_code'):
            from_pos = True
        return super(StockPicking, self.with_context(from_pos=from_pos))._action_done()
