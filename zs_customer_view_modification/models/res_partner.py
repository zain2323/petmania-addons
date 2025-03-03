from dateutil.relativedelta import relativedelta
from odoo import fields, models, tools, api, _
from collections import defaultdict
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_category = fields.Selection([
        ('prestige', 'Prestige'),
        ('platinum', 'Platinum'),
        ('gold', 'Gold')
    ], string='Customer Category', default='gold')
    pet_ids = fields.One2many('vet.pet', 'owner_id', string='Pets')
    pet_count = fields.Integer(compute='_compute_pet_count', string='Pet Count')

    purchase_count = fields.Integer(compute='_compute_purchase_stats', string='Purchase Count')
    purchase_total = fields.Float(compute='_compute_purchase_stats', string='Total Purchases')
    frequent_products = fields.Many2many('product.product', compute='_compute_frequent_products',
                                         string='Frequent Products')

    revenue_stream_ids = fields.Many2many(
        'product.company.type',
        string='Revenue Streams (Last 6 months)',
    )

    def _compute_revenue_streams(self):
        half_year = fields.Date.to_string(fields.Date.today() - relativedelta(months=6))
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('date_order', '>=', half_year)
        ])
        partner_revenue_streams = defaultdict(set)

        for order in pos_orders:
            if order.partner_id:
                for line in order.lines:
                    product = line.product_id
                    if product.company_type:
                        partner_revenue_streams[order.partner_id].add(product.company_type.id)
        for partner, revenue_streams in partner_revenue_streams.items():
            partner.revenue_stream_ids = [(6, 0, list(revenue_streams))]

    def _update_customer_categories(self):
        # Define thresholds
        prestige_threshold = 50000
        platinum_threshold = 25000

        one_year_ago = fields.Date.to_string(fields.Date.today() - relativedelta(months=6))
        # Get total spending in the last year
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('date_order', '>=', one_year_ago)
        ])
        partner_revenues = defaultdict(float)
        for order in pos_orders:
            if order.partner_id:
                partner_revenues[order.partner_id] += order.amount_total
        for partner, revenues in partner_revenues.items():
            if revenues >= prestige_threshold:
                partner.customer_category = 'prestige'
            elif revenues >= platinum_threshold:
                partner.customer_category = 'platinum'
            else:
                partner.customer_category = 'gold'

    def _compute_purchase_stats(self):
        for partner in self:
            confirmed_orders = self.env['pos.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ])
            partner.purchase_count = len(confirmed_orders)
            partner.purchase_total = sum(order.amount_total for order in confirmed_orders)

    def _compute_frequent_products(self):
        for partner in self:
            confirmed_orders = self.env['pos.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ])

            # Count product frequencies
            product_counts = {}
            for order in confirmed_orders:
                for line in order.lines:
                    product_id = line.product_id.id
                    if product_id in product_counts:
                        product_counts[product_id] += line.qty
                    else:
                        product_counts[product_id] = line.qty

            # Sort by frequency and take top 5
            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            partner.frequent_products = self.env['product.product'].browse([p[0] for p in top_products])

    def _compute_pet_count(self):
        for partner in self:
            partner.pet_count = len(partner.pet_ids)

    def action_view_pets(self):
        self.ensure_one()
        return {
            'name': 'Pets',
            'type': 'ir.actions.act_window',
            'res_model': 'vet.pet',
            'view_mode': 'tree,form',
            'domain': [('owner_id', '=', self.id)],
            'context': {'default_owner_id': self.id},
        }
