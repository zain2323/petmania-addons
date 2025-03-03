# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_in_pos_company = fields.Boolean(
        "Available in POS (Company Specific)",
        default=True,
        company_dependent=True,
    )
