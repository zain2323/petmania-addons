# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to track reward purchases
        """
        # Call parent create method
        order_lines = super().create(vals_list)

        # Process each created order line
        for line in order_lines:
            # Get the order to access partner
            order = line.order_id

            # Skip if no partner
            if not order.partner_id:
                continue

            # Get or create reward tracking
            tracking = self.env['customer.reward.tracking'].get_or_create_tracking(
                order.partner_id,
                line.product_id
            )

            # If tracking exists, create purchase line
            if tracking:
                # Set first purchase date if not set
                if not tracking.first_purchase_date:
                    tracking.first_purchase_date = line.create_date

                # Create purchase line
                self.env['customer.reward.purchase.line'].create({
                    'tracking_id': tracking.id,
                    'pos_order_line_id': line.id,
                    'purchase_date': line.create_date,
                    'product_id': line.product_id.id,
                    'quantity': line.qty
                })

        return order_lines


class LoyaltyRewardConfig(models.Model):
    _name = 'loyalty.reward.config'
    _description = 'Loyalty Reward Configuration'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product',
        string='Eligible Product',
        required=True,
        help='Product that triggers the loyalty reward'
    )

    purchase_count = fields.Integer(
        string='Required Purchase Count',
        required=True,
        help='Number of times the product must be purchased to earn the reward',
        default=10
    )

    validity_days = fields.Integer(
        string='Validity Period (Days)',
        required=True,
        help='Number of days from the first purchase to accumulate the required count',
        default=20
    )

    def check_reward_streak(self, partner_id=None):
        """
        RPC method to check if a partner has completed a reward streak
        """
        # If no partner_id is provided, raise an error

        if not partner_id:
            return False

        # Find the specific tracking record for this partner and reward config
        tracking = self.env['customer.reward.tracking'].search([
            ('partner_id', '=', partner_id),
            ('reward_config_id', '=', self.id),
        ], limit=1)
        # If no tracking found, return False
        if not tracking:
            return False

        # Check streak and get reward
        reward_product = tracking.check_streak_and_get_reward()
        if reward_product:
            return {
                'product_id': reward_product.id,
                'reward_config_id': tracking.reward_config_id.id
            }

        return False

    @api.constrains('purchase_count', 'validity_days')
    def _check_positive_values(self):
        """
        Validate that purchase count and validity days are positive
        """
        for record in self:
            if record.purchase_count <= 0:
                raise ValidationError("Purchase Count must be greater than 0")
            if record.validity_days <= 0:
                raise ValidationError("Validity Days must be greater than 0")


class CustomerRewardTracking(models.Model):
    _name = 'customer.reward.tracking'
    _description = 'Customer Reward Tracking'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        help='Customer being tracked for rewards'
    )

    reward_config_id = fields.Many2one(
        'loyalty.reward.config',
        string='Reward Configuration',
        required=True,
        help='Reward configuration associated with this tracking'
    )

    purchase_line_ids = fields.One2many(
        'customer.reward.purchase.line',
        'tracking_id',
        string='Purchase Lines',
        help='Purchase lines contributing to the reward'
    )

    first_purchase_date = fields.Datetime(
        string='First Purchase Date',
        help='Date of the first purchase in the current tracking period'
    )

    def check_streak_and_get_reward(self):
        """
        Check if the customer is eligible for a reward based on total quantity purchased
        """
        self.ensure_one()

        # Sort purchase lines by purchase date in descending order
        sorted_lines = self.purchase_line_ids.filtered(
            lambda l: not l.is_redeemed
        ).sorted(key=lambda l: l.purchase_date, reverse=True)
        # Calculate total quantity of unredeemed purchases
        total_quantity = sum(line.quantity for line in sorted_lines)
        # Check if the total quantity meets the required purchase count
        if total_quantity >= self.reward_config_id.purchase_count:
            # Check if the purchases are within the validity period
            first_line = sorted_lines[-1]  # Last chronological line
            last_line = sorted_lines[0]  # Most recent line

            if (last_line.purchase_date - first_line.purchase_date).days <= self.reward_config_id.validity_days:
                # Determine how many lines to mark as redeemed
                quantity_to_redeem = self.reward_config_id.purchase_count
                redeemed_quantity = 0
                lines_to_redeem = []

                # Go through sorted lines to accumulate quantity
                for line in sorted_lines:
                    if redeemed_quantity >= quantity_to_redeem:
                        break

                    # Add this line to redemption
                    lines_to_redeem.append(line)
                    redeemed_quantity += line.quantity

                # Mark the selected lines as redeemed
                self.env['customer.reward.purchase.line'].browse(
                    [line.id for line in lines_to_redeem]
                ).redeem_reward()

                # Return the reward product
                return self.reward_config_id.product_id

        return False

    @api.model
    def get_or_create_tracking(self, partner, product):
        """
        Get or create a reward tracking for a customer and product
        """
        # Find applicable reward configuration
        reward_config = self.env['loyalty.reward.config'].search([
            ('product_id', '=', product.id)
        ], limit=1)

        # If no reward config exists, return False
        if not reward_config:
            return False

        # Search for existing tracking
        tracking = self.search([
            ('partner_id', '=', partner.id),
            ('reward_config_id', '=', reward_config.id)
        ], limit=1)

        # Create if not exists
        if not tracking:
            tracking = self.create({
                'partner_id': partner.id,
                'reward_config_id': reward_config.id
            })

        return tracking


class CustomerRewardPurchaseLine(models.Model):
    _name = 'customer.reward.purchase.line'
    _description = 'Customer Reward Purchase Line'

    tracking_id = fields.Many2one(
        'customer.reward.tracking',
        string='Reward Tracking',
        required=True,
        ondelete='cascade'
    )

    pos_order_line_id = fields.Many2one(
        'pos.order.line',
        string='POS Order Line',
        help='Related POS Order Line'
    )

    purchase_date = fields.Datetime(
        string='Purchase Date',
        required=True,
        help='Date of the purchase'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help='Product purchased'
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        help='Quantity of product purchased'
    )

    is_redeemed = fields.Boolean(
        string='Redeemed',
        default=False,
        help='Indicates if this purchase line has been used for reward redemption'
    )

    def redeem_reward(self):
        """
        Mark the purchase lines as redeemed
        """
        return self.write({'is_redeemed': True})
