from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class DefaultLocations(models.Model):
    _name = "default.locations"
    _description = "Default Locations"
    
    location_ids = fields.Many2many(
        comodel_name="stock.location", string="Locations", required=True
    )
    name = fields.Char("name")
    