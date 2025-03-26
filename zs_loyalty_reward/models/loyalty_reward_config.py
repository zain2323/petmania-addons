# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
