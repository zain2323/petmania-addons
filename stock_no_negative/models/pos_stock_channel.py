# -*- coding: utf-8 -*-

from odoo import api, fields, models
from collections import deque


class PosStockChannel(models.TransientModel):
    _name = 'stock.update'

    # def broadcast(self, stock_quant):
    #     data = stock_quant.read(['product_id', 'location_id', 'available_quantity'])
    #     self.env['bus.bus']._sendmany([[(self._cr.dbname, 'stock.update', self.env.user.id), 'stock_update', data]])

    def broadcast(self, stock_quant):
        data = stock_quant.read(['product_id', 'location_id', 'available_quantity'])
        if data and len(data) > 0:
            pos_session = self.env['pos.session'].search(
                [('state', 'in', ['opened', 'opening_control'])])
            if pos_session:
                for each_session in pos_session:
                    self.env['bus.bus']._sendmany([[(self._cr.dbname, 'stock.update', each_session.user_id.id), 'stock_update', data]])
