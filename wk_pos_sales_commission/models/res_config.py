# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_commission_id = fields.Many2one('pos.sale.commission', string="Default Commission")
    commission_product_id = fields.Many2one('product.product', string="Commission Product")
    use_pos_congif_commission = fields.Boolean(string="Use POS Config Commission")
    auto_confirm_at_order_validation = fields.Boolean(string="Auto Confirm at Order Validation")
    create_commission = fields.Selection([
        ('single', 'Commission by Order'),
        ('multiple', 'Commission by Product')],
        default='single', string='Commission')

    @api.model
    def res_config_settings_enable(self):
        enable_env = self.env['res.config.settings'].create({'sale_commission_id': self.env.ref('wk_pos_sales_commission.pos_sale_commission_1').id,
                                                            'commission_product_id': self.env.ref('wk_pos_sales_commission.commission_product_1').id})
        enable_env.execute()
 
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'sale_commission_id',self.sale_commission_id.id)
        IrDefault.set('res.config.settings', 'commission_product_id',self.commission_product_id.id)
        IrDefault.set('res.config.settings', 'use_pos_congif_commission',self.use_pos_congif_commission)     
        IrDefault.set('res.config.settings', 'auto_confirm_at_order_validation',self.auto_confirm_at_order_validation)        
        IrDefault.set('res.config.settings', 'create_commission',self.create_commission)        
        return True

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
            'commission_product_id':IrDefault.get('res.config.settings', 'commission_product_id') or False,
            'sale_commission_id':IrDefault.get('res.config.settings', 'sale_commission_id') or False,
            'use_pos_congif_commission':IrDefault.get('res.config.settings', 'use_pos_congif_commission') or False,            
            'auto_confirm_at_order_validation':IrDefault.get('res.config.settings', 'auto_confirm_at_order_validation') or False,            
            'create_commission':IrDefault.get('res.config.settings', 'create_commission') or 'single',            
            }
        )
        return res
