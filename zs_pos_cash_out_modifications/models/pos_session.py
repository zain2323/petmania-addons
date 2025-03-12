from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    is_cashed_out = fields.Boolean(string="Is Cashed Out First?", default=False)
    is_cashed_out_last = fields.Boolean(string="Is Cashed Out Last?", default=False)
