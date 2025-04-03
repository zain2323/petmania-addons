# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


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
            to_suspend = config.product_ids.filtered(lambda p: p.id not in purchased_product_ids and not p.is_suspended)

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
