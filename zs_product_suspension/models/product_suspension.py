# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductSuspensionConfig(models.Model):
    _name = 'product.suspension.config'
    _description = 'Product Suspension Configuration'
    name = fields.Char('Name', required=True)
    product_ids = fields.Many2many('product.product', string='Product')
    days_no_purchase = fields.Integer(
        string='Days Without Purchase',
        help='Number of days without purchase to suspend a product'
    )
    invoice_streak = fields.Integer(
        string='Invoice Streak',
        help='Number of times not invoiced from vendor consecutively but was present in RFQ'
    )

    def unlink(self):
        products = self.env['product.template'].search([('suspension_config', '=', self.id)])
        products.action_unsuspend_product()
        return super(ProductSuspensionConfig, self).unlink()

    @api.model
    def cron_suspend_products(self):
        """Suspend products with no purchase in x days"""
        configs = self.env['product.suspension.config'].search([])

        for config in configs:
            if not config.days_no_purchase:
                return

            #  suspending products not purchased in x days
            cutoff_date = (datetime.now() + timedelta(hours=5)) - timedelta(days=config.days_no_purchase)
            # Get products that have been purchased recently
            purchased_product_ids = self.env['purchase.order.line'].search([
                ('order_id.state', '=', 'purchase'),
                ('create_date', '>=', cutoff_date),
                ('product_id', 'in', config.product_ids.ids)
            ]).mapped('product_id.id')

            # Determine products to suspend (those in config but NOT in purchased products)
            to_suspend = config.product_ids.filtered(
                lambda p: p.id not in purchased_product_ids and not p.is_suspended and p.create_date and
                          p.create_date <= cutoff_date)

            # Suspend the products
            to_suspend.write({
                'is_suspended': True,
                'suspension_date': fields.Datetime.now(),
                'suspension_reason': "Not purchased in specified days",
                'suspension_config': config.id
            })

            # TODO implement streak


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_suspended = fields.Boolean(
        string='Suspended',
        default=False,
        tracking=True
    )
    suspension_date = fields.Datetime(
        string='Suspension Date',
        tracking=True
    )
    suspension_reason = fields.Char(string="Suspension Reason")
    suspension_config = fields.Many2one('product.suspension.config', string='Suspension Configuration')
    conversion_rate = fields.Float(string="Conversion Rate", compute="_compute_conversion_rate")

    def get_out_of_stock_date(self):
        last_out_of_stock_move = self.env['stock.move'].search([
            ('product_id', '=', self.id),
            ('state', '=', 'done'),
            ('product_uom_qty', '>', 0),
            ('company_id', '=', self.env.company.id)
        ], order="date DESC", limit=1)

        if last_out_of_stock_move:
            last_out_of_stock_date = last_out_of_stock_move.date.date()
        else:
            last_out_of_stock_date = datetime.now().date()

        return last_out_of_stock_date

    @api.depends('qty_available')
    def _compute_conversion_rate(self):
        StockMove = self.env['stock.move']
        POSLine = self.env['pos.order.line']
        today = fields.Date.today()
        two_years_ago = today - timedelta(days=730)

        for product in self:
            incoming_moves = StockMove.search([
                ('product_id', '=', product.id),
                ('date', '>=', two_years_ago),
                ('location_dest_id.usage', '=', 'internal'),
                ('location_id.usage', '=', 'supplier'),
                ('state', '=', 'done')
            ], order='date asc', limit=1)

            if not incoming_moves:
                product.conversion_rate = 0.0
                continue

            latest_stock_in_date = incoming_moves.date.date()

            if product.qty_available > 0:
                in_stock_last_date = today
            else:
                in_stock_last_date = self.get_out_of_stock_date()

            days_diff = (in_stock_last_date - latest_stock_in_date).days or 1
            _logger.critical(f"Stock In: {latest_stock_in_date}")
            _logger.critical(f"Out of stock date: {in_stock_last_date}")
            pos_lines = POSLine.search([
                ('product_id', '=', product.id),
                ('order_id.date_order', '>=', latest_stock_in_date),
                ('order_id.date_order', '<=', in_stock_last_date),
                ('order_id.state', 'in', ['paid', 'done', 'invoiced'])
            ])
            sold_qty = sum(pos_lines.mapped('qty'))
            _logger.critical(f"sold qty {sold_qty}")

            product.conversion_rate = sold_qty / days_diff

    def action_suspend_product(self, reason='manual'):
        """Manual product suspension"""
        for product in self:
            product.write({
                'is_suspended': True,
                'suspension_date': fields.Datetime.now(),
                "suspension_reason": reason,
            })
        return True

    def action_unsuspend_product(self):
        """Unsuspend products"""
        for product in self:
            product.write({
                'is_suspended': False,
                'suspension_date': False,
                'suspension_reason': ''
            })
        return True


class Brand(models.Model):
    _inherit = 'product.brand'

    is_discontinued = fields.Boolean(
        string='Discontinued',
        default=False
    )

    def write(self, vals):
        discontinued_changed = 'is_discontinued' in vals
        result = super().write(vals)
        if discontinued_changed:
            for brand in self:
                products = self.env['product.template'].search([
                    ('product_brand_id', '=', brand.id)
                ])
                if brand.is_discontinued:
                    products.action_suspend_product(reason='Brand discontinued')
                else:
                    products.action_unsuspend_product()
        return result


class Vendor(models.Model):
    _inherit = 'vendor.name'

    is_discontinued = fields.Boolean(
        string='Discontinued',
        default=False
    )

    def write(self, vals):
        discontinued_changed = 'is_discontinued' in vals
        result = super().write(vals)
        if discontinued_changed:
            for vendor in self:
                products = self.env['product.template'].search([
                    ('product_vendor_name_id', '=', vendor.id)
                ])
                if vendor.is_discontinued:
                    products.action_suspend_product(reason='Vendor discontinued')
                else:
                    products.action_unsuspend_product()
        return result
