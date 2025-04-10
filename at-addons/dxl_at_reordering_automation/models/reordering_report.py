# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class ReorderingReportLine(models.Model):
    _name = "reordering.report.line"
    _description = "Reordering Report Line"

    name = fields.Char('Product Name', compute="_compute_name", store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', required=True)
    product_id = fields.Many2one('product.product', string="Product Name")
    barcode = fields.Char(string="Barcode", related='product_id.barcode', store=True)
    standard_price = fields.Float(string='Cost', related='product_id.standard_price')
    product_brand_id = fields.Many2one('product.brand', string="Brand", related="product_id.product_brand_id")
    category_id = fields.Many2one('product.category', string="Category")
    display_category = fields.Char('Category', compute="_compute_display_category")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    display_sub_category = fields.Char('Sub Category', compute="_compute_display_sub_category")
    sales_data = fields.Integer(string="Sales Data(in Days)")
    sales_data_in_days = fields.Char(string="Sales Data(in Days)", compute="_compute_sales_data_in_days")
    avg_sales = fields.Float(string="Avg. Sales/Day", compute='_compute_avg_sales', store=True)
    req_storage = fields.Integer(string="Req Storage (in Days)")
    req_storage_in_days = fields.Char(string="Req Storage", compute='_compute_req_storage_in_days')
    req_storage_level_new = fields.Integer(string="Req. Storage Level", compute='_compute_avg_sales', store=True)
    desired_investment = fields.Float(string="Desired Investment", compute='_compute_desired_investment')
    present_stock = fields.Float(string="Present Stock", compute="_compute_present_stock")
    present_invenstment = fields.Float(string="Present Investment", compute="_compute_present_invenstment")
    excess_stock = fields.Float(string="Excess Stock", compute='_compute_excess_stock')
    excess_investment = fields.Float(string="Excess  Investment", compute='_compute_excess_investment')
    deficient_stock = fields.Float(string="Deficient Stock", compute='_compute_deficient_stock')
    deficient_investment = fields.Float(string="Deficient Investment", compute='_compute_deficient_investment')
    return_excess_qty = fields.Float(string="Return Excess Qty", compute='_compute_return_excess_qty')
    manual_return_excess_qty = fields.Float(string="Manual Return of Excess Qty")
    order_deficient_qty = fields.Float(string="Order Deficient Qty", compute='_compute_order_deficient_qty')
    manually_order_deficient_qty = fields.Float(string="Manually Ordered Deficient Qty")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    date = fields.Date(required=True, default=lambda self: fields.Date.context_today(self))
    reason = fields.Char(string='Reason')

    @api.depends('sales_data', 'warehouse_id', 'product_id', 'req_storage')
    def _compute_avg_sales(self):
        for line in self:
            sale_back_date = line.create_date - relativedelta(days=line.sales_data)
            sale_moves = self.env['stock.move'].sudo().search([('location_id', '=', line.warehouse_id.lot_stock_id.id), ('location_id.usage', '=', 'internal'), ('location_dest_id.usage', '=', 'customer'), ('product_id', '=', line.product_id.id), ('date', '>=', sale_back_date), ('state', '=', 'done')])
            avg_sales = sum(sale_moves.mapped('product_uom_qty')) / line.sales_data if line.sales_data > 0 else 0
            line.avg_sales = avg_sales
            line.req_storage_level_new = avg_sales * line.req_storage

    @api.constrains('manual_return_excess_qty', 'manually_order_deficient_qty')
    def _check_validation_manual_qty(self):
        if self.state == 'posted':
            raise ValidationError(_('You cannot change posted records!'))

    @api.depends('deficient_stock')
    def _compute_order_deficient_qty(self):
        for line in self:
            line.order_deficient_qty = line.deficient_stock

    @api.depends('excess_stock')
    def _compute_return_excess_qty(self):
        for line in self:
            line.return_excess_qty = line.excess_stock

    @api.depends('standard_price', 'deficient_stock')
    def _compute_deficient_investment(self):
        for line in self:
            line.deficient_investment = line.standard_price * line.deficient_stock

    @api.depends('req_storage_level_new', 'present_stock')
    def _compute_deficient_stock(self):
        for line in self:
            deficient_stock = line.req_storage_level_new - line.present_stock
            if deficient_stock > 0:
                line.deficient_stock = deficient_stock
            else:
                line.deficient_stock = 0

    @api.depends('standard_price', 'excess_stock')
    def _compute_excess_investment(self):
        for line in self:
            line.excess_investment = line.standard_price * line.excess_stock

    @api.depends('warehouse_id', 'product_id')
    def _compute_present_stock(self):
        for line in self:
            line.present_stock = line.product_id.with_context(warehouse=line.warehouse_id.id).qty_available

    @api.depends('present_stock', 'standard_price')
    def _compute_present_invenstment(self):
        for line in self:
            line.present_invenstment = line.present_stock * line.standard_price

    @api.depends('present_stock', 'req_storage_level_new')
    def _compute_excess_stock(self):
        for line in self:
            excess_stock = line.present_stock - line.req_storage_level_new
            if excess_stock > 0:
                line.excess_stock = excess_stock
            else:
                line.excess_stock = 0

    @api.depends('standard_price', 'req_storage_level_new')
    def _compute_desired_investment(self):
        for line in self:
            line.desired_investment = line.req_storage_level_new * line.standard_price

    @api.depends('req_storage')
    def _compute_req_storage_in_days(self):
        for line in self:
            line.req_storage_in_days = str(line.req_storage) + ' Days'

    @api.depends('sales_data')
    def _compute_sales_data_in_days(self):
        for line in self:
            line.sales_data_in_days = str(line.sales_data) + ' Days'

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            line.name = line.product_id.name

    def action_posted_records(self):
        self.write({'state': 'posted'})

    @api.depends('category_id')
    def _compute_display_category(self):
        for line in self:
            line.display_category = line.category_id.name

    @api.depends('sub_category_id')
    def _compute_display_sub_category(self):
        for line in self:
            line.display_sub_category = line.sub_category_id.name

    def unlink(self):
        if self.filtered(lambda x: x.state == 'posted'):
            raise ValidationError(_('You cannot delete posted records!'))
        return super(ReorderingReportLine, self).unlink()
