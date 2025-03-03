from odoo import fields, models, api, _, registry, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    scm_grading_id = fields.Many2one("scm.grading", related="product_id.product_scm_grading_id")
