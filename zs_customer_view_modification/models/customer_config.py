from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class CustomerCategoryConfig(models.Model):
    _name = 'customer.category.config'
    _description = 'Customer Category Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(default=True)

    # Duration settings
    duration_type = fields.Selection([
        ('monthly', 'Last 30 days'),
        ('quarterly', 'Last 90 days'),
        ('biannual', 'Last 180 days'),
        ('yearly', 'Last 365 days'),
        ('lifetime', 'Life Time'),
    ], string='Duration', required=True, default='yearly')

    # Criteria type
    criteria_type = fields.Selection([
        ('value', 'By Order Value'),
        ('count', 'By Number of Orders'),
    ], string='Criteria Type', required=True, default='value')

    # Threshold lines (for different categories)
    threshold_line_ids = fields.One2many('customer.category.threshold.line', 'config_id', string='Category Thresholds')


class CustomerCategoryThresholdLine(models.Model):
    _name = 'customer.category.threshold.line'
    _description = 'Customer Category Threshold Line'
    _order = 'threshold_value desc'

    config_id = fields.Many2one('customer.category.config', string='Configuration', required=True, ondelete='cascade')
    category = fields.Selection([
        ('platinum', 'Platinum'),
        ('prestige', 'Prestige'),
    ], string='Category', required=True)
    threshold_value = fields.Float(string='Threshold Value', required=True,
                                   help='Minimum amount or number of orders required to qualify')
    sequence = fields.Integer(string='Sequence', default=10)

    _sql_constraints = [
        ('category_config_unique', 'unique(config_id, category)',
         'Each category can only have one threshold per configuration!')
    ]


class CustomerTagConfig(models.Model):
    _name = 'customer.tag.config'
    _description = 'Customer Tag Configuration'

    name = fields.Char(string='Tag Name', required=True)
    active = fields.Boolean(default=True)
    product_category_id = fields.Many2many('product.category', string='Product Category', required=True)
    # Duration settings
    duration_type = fields.Selection([
        ('monthly', 'Last 30 days'),
        ('quarterly', 'Last 90 days'),
        ('biannual', 'Last 180 days'),
        ('yearly', 'Last 365 days'),
        ('lifetime', 'Life Time'),
    ], string='Duration', required=True, default='yearly')
    criteria_type = fields.Selection([
        ('value', 'By Order Value'),
        ('count', 'By Number of Orders'),
    ], string='Criteria Type', required=True, default='value')

    threshold_value = fields.Float(string='Threshold Value', required=True,
                                   help='Minimum amount or number of orders required to qualify')

class GIftCardInherit(models.Model):
    _inherit='gift.card'

    config_id = fields.Many2one('gift.card.config', string='Gift Card Configuration')

    def get_applicable_products(self):
        domain = []
        if self.config_id.franchise_division_ids:
            domain.append(('company_type', 'in', self.config_id.franchise_division_ids.ids))

        if self.config_id.product_division_ids:
            domain.append(('product_division_id', 'in', self.config_id.product_division_ids.ids))

        if self.config_id.product_category_ids:
            domain.append(('categ_id', 'in', self.config_id.product_category_ids.ids))

        if self.config_id.product_brand_ids:
            domain.append(('product_brand_id', 'in', self.config_id.product_brand_ids.ids))

        if self.config_id.product_ids:
            domain.append(('id', 'in', self.config_id.product_ids.ids))

        products = self.env['product.product'].search(domain)
        return products.ids

class GiftCardConfig(models.Model):
    _name = 'gift.card.config'
    _description = 'Gift Card Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(default=True)

    # Gift card amount settings
    gift_card_amount = fields.Float(string='Gift Card Amount', required=True,
                                    help='Amount to be loaded on generated gift cards')
    # applicability
    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')

    # Customer category requirements
    customer_category = fields.Selection([
        ('prestige', 'Prestige'),
        ('platinum', 'Platinum'),
        ('gold', 'Gold')
    ], string='Customer Category', required=True)

    # Customer tags requirements
    customer_tag_ids = fields.Many2many('customer.tag.config', string='Required Customer Tags',
                                        help='Customer must have all these tags to qualify')

    # Optional setting for validity
    validity_days = fields.Integer(string='Validity (Days)', default=365,
                                   help='Number of days the gift card will be valid after generation')

    # Relation to track which customers received gift cards from this config
    gift_card_history_ids = fields.One2many('gift.card.generation.history', 'config_id',
                                            string='Gift Card Generation History')

    def action_generate_gift_cards(self):
        """Generate gift cards for eligible customers"""
        self.ensure_one()

        # Find eligible customers matching the configuration criteria
        domain = [('customer_category', '=', self.customer_category)]

        eligible_customers = self.env['res.partner'].search(domain)

        # Filter customers by required tags
        if self.customer_tag_ids:
            eligible_customers = eligible_customers.filtered(
                lambda partner: all(tag in partner.customer_tag_ids.ids for tag in self.customer_tag_ids.ids)
            )

        if not eligible_customers:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Eligible Customers',
                    'message': 'No customers found matching the category and tag requirements.',
                    'sticky': False,
                    'type': 'warning',
                }
            }

        # Get customers who already received gift cards from this config
        already_received_customer_ids = self.gift_card_history_ids.mapped('partner_id.id')

        # Filter out customers who already received gift cards
        new_eligible_customers = eligible_customers.filtered(
            lambda partner: partner.id not in already_received_customer_ids
        )

        if not new_eligible_customers:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No New Eligible Customers',
                    'message': 'All eligible customers have already received gift cards from this configuration.',
                    'sticky': False,
                    'type': 'warning',
                }
            }

        # Calculate expiration date
        if self.validity_days:
            expiration_date = fields.Date.add(fields.Date.today(), days=self.validity_days)
        else:
            expiration_date = fields.Date.add(fields.Date.today(), years=1)

        # Generate gift cards for eligible customers
        created_gift_cards = self.env['gift.card']
        for customer in new_eligible_customers:
            gift_card_vals = {
                'partner_id': customer.id,
                'initial_amount': self.gift_card_amount,
                'expired_date': expiration_date,
                'company_id': self.env.company.id,
                'config_id': self.id,
            }
            gift_card = self.env['gift.card'].create(gift_card_vals)

            # Record the gift card generation in history
            self.env['gift.card.generation.history'].create({
                'config_id': self.id,
                'partner_id': customer.id,
                'gift_card_id': gift_card.id,
                'generation_date': fields.Date.today(),
            })

            created_gift_cards += gift_card

        # Return a notification or action to view the created gift cards
        if created_gift_cards:
            return {
                'name': 'Generated Gift Cards',
                'type': 'ir.actions.act_window',
                'res_model': 'gift.card',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_gift_cards.ids)],
                'context': {'create': False},
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Gift Card Generation',
                    'message': 'No new gift cards were generated.',
                    'sticky': False,
                    'type': 'warning',
                }
            }


class GiftCardGenerationHistory(models.Model):
    _name = 'gift.card.generation.history'
    _description = 'Gift Card Generation History'
    _order = 'generation_date desc, id desc'

    config_id = fields.Many2one('gift.card.config', string='Gift Card Configuration',
                                required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 required=True, ondelete='cascade', index=True)
    gift_card_id = fields.Many2one('gift.card', string='Gift Card',
                                   required=True, ondelete='cascade')
    generation_date = fields.Date(string='Generation Date', required=True, default=fields.Date.today)

    _sql_constraints = [
        ('unique_config_partner', 'UNIQUE(config_id, partner_id)',
         'A customer can only receive one gift card per configuration!')
    ]
