from odoo import api, fields, models


class FFAgent(models.Model):
    _name = "ff.agent"
    _order = "name"

    name = fields.Char("FF Agent", required=True)


class CLAgent(models.Model):
    _name = "cl.agent"
    _order = "name"

    name = fields.Char("CL Agent", required=True)


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    cc_agent = fields.Many2one('cl.agent', string="CC Agent")
    ff_agent = fields.Many2one('ff.agent', string="FF Agent")