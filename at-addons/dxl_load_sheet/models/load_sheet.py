# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class LoadSheet(models.Model):
    _name = "load.sheet"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Load Sheet"

    name = fields.Char('Sequence No', default='NEW', readonly=True, required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Posted')], default='draft', required=True, string="Status")
    sale_order_ids = fields.Many2many('sale.order', string="Sale Orders")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    load_sheet_lines = fields.One2many('load.sheet.line', 'load_sheet_id', string='Load Sheet Lines', copy=True, auto_join=True, states={'draft': [('readonly', False)]}, readonly=True)
    is_supervisor = fields.Boolean(compute="_compute_is_supervisor")
    is_admin = fields.Boolean(compute="_compute_is_supervisor")
    sales_orders = fields.Char(compute="_compute_sales_orders", store=True, string="Quotation Reference No.s")

    @api.depends('sale_order_ids')
    def _compute_sales_orders(self):
        for load_sheet in self:
            load_sheet.sales_orders = ','.join(load_sheet.sale_order_ids.mapped('name'))

    def _compute_is_supervisor(self):
        for sheet in self:
            is_supervisor = self.env.user.has_group('dxl_load_sheet.group_load_sheet_supervisor')
            is_admin = self.env.user.has_group('dxl_load_sheet.group_load_sheet_admin')
            sheet.is_supervisor = is_supervisor
            sheet.is_admin = is_admin

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'NEW':
                vals['name'] = self.env['ir.sequence'].next_by_code('seq.load.sheet')
        return super(LoadSheet, self).create(vals_list)

    def action_done(self):
        self.write({'state': 'done'})

    def action_reset(self):
        self.write({'state': 'draft'})


class LoadSheetLine(models.Model):
    _name = 'load.sheet.line'
    _description = 'Load Sheet Line'

    load_sheet_id = fields.Many2one('load.sheet', string='Load Sheet', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    company_id = fields.Many2one(related='load_sheet_id.company_id', string='Company', store=True, index=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    weight = fields.Float(string="Weight", related="product_id.weight", store=True)
    available_qty = fields.Float(string='Available Quantity', digits='Product Unit of Measure')
    difference = fields.Float(string='Difference', digits='Product Unit of Measure', compute="_compute_difference", store=True)

    @api.depends('available_qty', 'quantity')
    def _compute_difference(self):
        for line in self:
            line.difference = line.available_qty - line.quantity
