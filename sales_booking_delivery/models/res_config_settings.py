# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delivery_control = fields.Boolean(related='company_id.delivery_control', string='Enable Delivery Control', readonly=False)

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     get_param = self.env['ir.config_parameter'].sudo().get_param
    #     res.update(enable_combo=get_param('sales_booking_delivery.delivery_control'))
    #     return res

    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     set_param = self.env['ir.config_parameter'].sudo().set_param
    #     set_param('sales_booking_delivery.delivery_control', self.enable_combo)
