# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    def _compute_pos_sale_commission(self):
        commissions = self.env['pos.commission'].search([('employee_id', '=', self.id)])
        count = 0
        for commission in commissions:
            if(commission.employee_id.id == self.id):
                count = count + 1

        self.pos_sale_commission_total = count

    is_commission_applicable = fields.Boolean(string='Commission Applicable')
    pos_sale_commission_total = fields.Integer(compute='_compute_pos_sale_commission', string='Commission')