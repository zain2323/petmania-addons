# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class ProductSuspensionConfig(models.Model):
    _name = 'product.suspension.config'
    _description = 'Product Suspension Configuration'

    product_id = fields.Many2one('product.product', string='Product')
    days_no_purchase = fields.Integer(
        string='Days Without Purchase',
        help='Number of days without purchase to suspend a product'
    )
    invoice_streak = fields.Integer(
        string='Invoice Streak',
        help='Number of times not invoiced from vendor consecutively but was present in RFQ'
    )

    @api.model
    def cron_suspend_products(self):
        """Suspend products with no purchase in x days"""
        configs = self.env['product.suspension.config'].search([])

        for config in configs:
            if not config.days_no_purchase:
                return

            #  suspending products not purchased in x days
            cutoff_date = (datetime.now() + timedelta(hours=5)) - timedelta(days=config.days_no_purchase)
            purchase_orders = self.env['purchase.order'].search(
                [('state', '=', 'purchase'), ('create_date', '>=', cutoff_date)])
            is_purchased = False
            for po in purchase_orders:
                lines = po.order_line.filtered(lambda l: l.product_id.id == config.product_id.id)
                # if any purchase exist then breaking out of loop since the product is purchased
                if lines:
                    is_purchased = True
                    break
            # if not purchased and is not suspended already
            if config.product_id.purchase_ok and not config.product_id.is_suspended and not is_purchased:
                config.product_id.is_suspended = True

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

    def action_suspend_product(self, reason=False):
        """Manual product suspension"""
        for product in self:
            product.write({
                'is_suspended': True,
                'suspension_date': fields.Datetime.now()
            })
        return True

    def action_unsuspend_product(self):
        """Unsuspend products"""
        for product in self:
            product.write({
                'is_suspended': False,
                'suspension_date': False
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
                    products.action_suspend_product()
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
                    products.action_suspend_product()
                else:
                    products.action_unsuspend_product()
        return result
