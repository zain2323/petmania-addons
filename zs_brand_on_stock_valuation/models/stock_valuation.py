# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date
from datetime import datetime, timedelta


class StockValuation(models.Model):
    _inherit = "stock.valuation.layer"
    
    brand_id = fields.Char(
        string="Brand", help="Select a brand for this product",
        related='product_tmpl_id.product_brand_id.name',
        store=True
    )