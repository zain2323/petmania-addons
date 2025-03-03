# -*- coding: utf-8 -*-

from odoo import api, fields, models
from collections import deque


class PosConfig(models.Model):
    _inherit = 'pos.config'

    restrict_out_of_stock = fields.Boolean(
        string='Restrict Out of Stock on POS',
    )
