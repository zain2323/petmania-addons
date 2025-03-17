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
