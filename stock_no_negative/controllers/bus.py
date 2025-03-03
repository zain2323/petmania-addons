# -*- coding: utf-8 -*-
from odoo.http import request
from odoo.addons.bus.controllers.main import BusController

class OrderSyncController(BusController):

    def _poll(self, dbname, channels, last, options):
        """Add the relevant channels to the BusController polling."""
        if options.get('stock.update'):
            channels = list(channels)
            lock_channel = (
                request.db,
                'stock.update',
                options.get('stock.update')
            )
            channels.append(lock_channel)
        return super(OrderSyncController, self)._poll(dbname, channels, last, options)
