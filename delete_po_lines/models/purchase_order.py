# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    select_all = fields.Boolean()

    @api.onchange('select_all')
    def onchange_select_all(self):
        if self.select_all:
            for line in self.order_line:
                line.update({
                    'mark': self.select_all
                })
        else:
            for line in self.order_line:
                line.update({
                    'mark': self.select_all
                })

    def action_delete(self):
        if self.state != 'purchase':
            for line in self.order_line:
                if line.mark:
                    line.unlink()
        else:
            raise ValidationError(_("Lines Can not be deleted once PO confirm"))




class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mark = fields.Boolean()

