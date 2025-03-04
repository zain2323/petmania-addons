from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MinMaxConfig(models.Model):
    _name = 'min.max.config'
    _rec_name = 'name'

    product_id = fields.Many2one('product.product', string='Product')
    brand_id = fields.Many2one('product.brand', string='Brand')
    product_category_id = fields.Many2one('product.category', string='Product Category')
    product_division = fields.Many2one('product.division', string='Product Division')
    franchise_division = fields.Many2one('product.company.type', string='Franchise')
    min_qty = fields.Float(string='Min Quantity')
    max_qty = fields.Float(string='Max Quantity')
    company_id = fields.Many2one('res.company', string='Company', null=True)
    child_ids = fields.One2many(comodel_name='min.max.config.lines', inverse_name='config_id', string='Line ids')

    name = fields.Char(string='Name', compute='_compute_name', store=True)

    @api.depends('franchise_division', 'product_division', 'product_category_id', 'product_id')
    def _compute_name(self):
        for rec in self:
            rec.name = False
            if rec.franchise_division:
                rec.name = rec.franchise_division.name
            if rec.product_division:
                rec.name = rec.product_division.name
            if rec.product_category_id:
                rec.name = rec.product_category_id.name
            if rec.brand_id:
                rec.name = rec.brand_id.name
            if rec.product_id:
                rec.name = rec.product_id.name

    @api.model
    def create(self, vals):
        result = super(MinMaxConfig, self).create(vals)
        if not result.product_id:
            # create lines
            lines_data = [
                {'min_price': 1, 'max_price': 1000, 'config_id': result.id, 'min_qty': 1, 'max_qty': 10},
                {'min_price': 1001, 'max_price': 2000, 'config_id': result.id, 'min_qty': 11, 'max_qty': 20},
                {'min_price': 2001, 'max_price': 5000, 'config_id': result.id, 'min_qty': 21, 'max_qty': 30},
                {'min_price': 5001, 'max_price': 10000, 'config_id': result.id, 'min_qty': 31, 'max_qty': 40},
                {'min_price': 10001, 'max_price': 20000, 'config_id': result.id, 'min_qty': 41, 'max_qty': 50},
                {'min_price': 20001, 'max_price': 30000, 'config_id': result.id, 'min_qty': 51, 'max_qty': 60},
                {'min_price': 30001, 'max_price': 50000, 'config_id': result.id, 'min_qty': 61, 'max_qty': 70},
                {'min_price': 50001, 'max_price': 100000, 'config_id': result.id, 'min_qty': 71, 'max_qty': 80},
            ]
            line_ids = []
            for line in lines_data:
                line_id = self.env['min.max.config.lines'].create(line)
                line_ids.append(line_id)

        return result


class MinMaxConfigLines(models.Model):
    _name = 'min.max.config.lines'
    config_id = fields.Many2one('min.max.config', string='Config')
    min_qty = fields.Integer(string="Minimum QTY", default=0)
    max_qty = fields.Integer(string="Maximum QTY", default=0)
    min_price = fields.Float(string="Minimum Price", default=0)
    max_price = fields.Float(string="Maximum Price", default=0)


class MinMaxConfigByStorage(models.Model):
    _name = 'min.max.config.storage'
    _rec_name = 'name'

    product_id = fields.Many2one('product.product', string='Product')
    brand_id = fields.Many2one('product.brand', string='Brand')
    product_category_id = fields.Many2one('product.category', string='Product Category')
    product_division = fields.Many2one('product.division', string='Product Division')
    franchise_division = fields.Many2one('product.company.type', string='Franchise')
    min_days = fields.Integer(string="Minimum Days", default=0)
    max_days = fields.Integer(string="Maximum Days", default=0)
    ageing_days = fields.Integer(string="Ageing Criteria", default=0)
    company_id = fields.Many2one('res.company', string='Company', null=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True)

    @api.depends('franchise_division', 'product_division', 'product_category_id', 'product_id')
    def _compute_name(self):
        for rec in self:
            rec.name = False
            if rec.franchise_division:
                rec.name = rec.franchise_division.name
            if rec.product_division:
                rec.name = rec.product_division.name
            if rec.product_category_id:
                rec.name = rec.product_category_id.name
            if rec.brand_id:
                rec.name = rec.brand_id.name
            if rec.product_id:
                rec.name = rec.product_id.name
