from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_bonded = fields.Boolean(string='Is Bonded', default=False)

    @api.constrains('is_bonded')
    def _constrains_is_bonded(self):
        for rec in self:
            already_bonded = self.env['stock.warehouse'].search([('id','!=',rec.id), ('is_bonded','=',True)])
            if already_bonded:
                raise ValidationError(f'Warehouse {already_bonded.name} is already a bonded warehouse.\nOnly 1 warehouse can become bonded warehouse at a time')
