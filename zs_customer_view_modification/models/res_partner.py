from dateutil.relativedelta import relativedelta
from odoo import fields, models, tools, api, _
from collections import defaultdict
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

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
    customer_tag_ids = fields.Many2many('customer.tag.config', string='Customer tags')

    revenue_stream_ids = fields.Many2many(
        'product.category',
        string='Revenue Streams',
    )

    def _update_customer_tags(self):
        partners = self.env['res.partner'].search([])
        partners.write({'customer_tag_ids': [(5, 0, 0)]})

        configs = self.env['customer.tag.config'].search([('active', '=', True)])
        tag_ids = defaultdict(list)
        for config in configs:
            if config.duration_type == 'monthly':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=1))
            elif config.duration_type == 'quarterly':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=3))
            elif config.duration_type == 'biannual':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=6))
            else:
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=12))

            pos_orders = self.env['pos.order'].search([
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('date_order', '>=', duration)
            ])

            partner_revenues = defaultdict(float)

            for order in pos_orders:
                if order.partner_id:
                    lines = order.lines.filtered(lambda l: l.product_id.categ_id.id == config.product_category_id.id)
                    for line in lines:
                        value = line.price_subtotal_incl if config.criteria_type == 'value' else 1
                        partner_revenues[order.partner_id] += value

            for partner, value in partner_revenues.items():
                if value >= config.threshold_value:
                    tag_ids[partner].append(config.id)

        for partner, tags in tag_ids.items():
            partner.customer_tag_ids = [(6, 0, list(tags))]

    def _compute_revenue_streams(self):
        partners = self.env['res.partner'].search([])
        partners.write({'revenue_stream_ids': [(5, 0, 0)]})

        duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=3))
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('date_order', '>=', duration)
        ])

        partner_revenue_streams = defaultdict(set)

        for order in pos_orders:
            if order.partner_id:
                for line in order.lines:
                    product = line.product_id
                    if product.detailed_type == 'service':
                        partner_revenue_streams[order.partner_id].add(product.categ_id.id)
        for partner, revenue_streams in partner_revenue_streams.items():
            partner.revenue_stream_ids = [(6, 0, list(revenue_streams))]

    def _update_customer_categories(self):
        configs = self.env['customer.category.config'].search([('active', '=', True)])

        for config in configs:
            if config.duration_type == 'monthly':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=1))
            elif config.duration_type == 'quarterly':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=3))
            elif config.duration_type == 'biannual':
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=6))
            else:
                duration = fields.Date.to_string(fields.Date.today() - relativedelta(months=12))

            threshold_lines = config.threshold_line_ids.sorted(lambda l: -l.threshold_value)

            # Get total spending in the last year
            pos_orders = self.env['pos.order'].search([
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('date_order', '>=', duration)
            ])

            partner_revenues = defaultdict(float)
            for order in pos_orders:
                if order.partner_id:
                    if config.criteria_type == 'value':
                        partner_revenues[order.partner_id] += order.amount_total
                    else:
                        partner_revenues[order.partner_id] += 1

            for partner, revenues in partner_revenues.items():
                if revenues >= threshold_lines[0].threshold_value:
                    query = f"""UPDATE res_partner SET customer_category = 'prestige' WHERE id = {partner.id}"""
                    self.env.cr.execute(query)
                elif revenues >= threshold_lines[1].threshold_value:
                    query = f"""UPDATE res_partner SET customer_category = 'platinum' WHERE id = {partner.id}"""
                    self.env.cr.execute(query)
                else:
                    query = f"""UPDATE res_partner SET customer_category = 'gold' WHERE id = {partner.id}"""
                    self.env.cr.execute(query)

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
