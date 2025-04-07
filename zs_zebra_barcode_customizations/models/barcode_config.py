from odoo import models, fields, api


class BarcodeConfig(models.Model):
    _inherit = 'tdzebrabarcode.configuration'

    min_max_display = fields.Boolean('Min/Max Display', default=True)
    min_max_size = fields.Char('Min Max FontSize', default=7)
