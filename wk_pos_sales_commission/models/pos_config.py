# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.depends()
    def _compute_is_pos_config_commission_enable(self):
        val = self.env['ir.default'].sudo().get('res.config.settings', 'use_pos_congif_commission')
        self.is_pos_config_commission_enable = val

    @api.depends()
    def _compute_auto_validate_pos_sale_commission(self):
        val = self.env['ir.default'].sudo().get('res.config.settings', 'create_invoice_at_order_validation')
        self.is_auto_validate_pos_sale_commission = val

    is_use_pos_commission = fields.Boolean(string='Enable POS Sale Commision', default=True)
    show_apply_commission = fields.Boolean(string='Show Apply Commission Button', default=True)
    use_different_commission =  fields.Boolean(string='Use Different Commission for POS Session')
    sale_commission_id = fields.Many2one('pos.sale.commission', string="Default Commission")
    is_pos_config_commission_enable = fields.Boolean(string='Use Pos Config', compute='_compute_is_pos_config_commission_enable')
    is_auto_validate_pos_sale_commission = fields.Boolean(string="Auto Validate POS Sale Commission", compute='_compute_auto_validate_pos_sale_commission')