# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _get_group_closing_control_restriction(self):
        return self.env.ref('dxl_closing_control_restriction_group.group_closing_control_restriction')

    group_closing_control_restriction = fields.Many2one('res.groups', string='Closing Control Restriction', default=_get_group_closing_control_restriction)
