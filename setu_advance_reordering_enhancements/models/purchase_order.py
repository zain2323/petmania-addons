from odoo import fields, models, api, _, registry, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    scm_grading_id = fields.Many2one("scm.grading")

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    scm_grading_id = fields.Many2one("scm.grading", string="SCM Grading", related="product_id.product_scm_grading_id")