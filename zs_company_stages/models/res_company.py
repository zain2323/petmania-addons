from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"

    stage = fields.Char(string="Company Stage", default="Embryonic")

    def compute_company_stage(self):
        companies = self.env['res.company'].search([])
        for rec in companies:
            pos_order = rec.env['pos.order'].search([('company_id', '=', rec.id), ('create_date', '!=', False)], limit=1, order='create_date asc')
            if not pos_order:
                continue
            created_date = pos_order.create_date.date()
            current_date = datetime.now().date()

            delta = (current_date - created_date).days
            _logger.critical(f"{rec.name}----{delta}")
            if 0 <= delta <= 90:
                rec.stage = "Embryonic"
            elif 91 <= delta <= 180:
                rec.stage = "Infancy"
            else:
                rec.stage = "Stable"
