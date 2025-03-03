# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_in_pos_company = fields.Boolean(
        "Available in POS (Company Specific)",
        default=True,
        company_dependent=True,
    )

    storage_config_id = fields.Many2one('min.max.config.storage', string='Min Config By Storage',
                                        compute="_compute_storage_config_id")
    value_config_id = fields.Many2one('min.max.config', string='Min Max Config By Value',
                                      compute="_compute_value_config_id")
    storage_config_basis = fields.Char(string='Storage Config Basis', compute='_compute_storage_config_id')
    value_config_basis = fields.Char(string='Value Config Basis', compute='_compute_value_config_id')

    def _compute_value_config_id(self):
        for rec in self:
            rec.value_config_id = False
            rec.value_config_basis = None
            value_config_franchise_division = rec.env['min.max.config'].search(
                [('franchise_division', '=', rec.company_type.id), ('product_id', '=', False),
                 ('product_category_id', '=', False), ('product_division', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_franchise_division and rec.company_type.id:
                rec.value_config_id = value_config_franchise_division.id
                rec.value_config_basis = "Franchise Division"
            # for product division
            value_config_product_division = rec.env['min.max.config'].search(
                [('product_division', '=', rec.product_division_id.id), ('product_id', '=', False),
                 ('product_category_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_product_division and rec.product_division_id:
                rec.value_config_id = value_config_product_division.id
                rec.value_config_basis = "Product Division"

            # for product category
            value_config_category = rec.env['min.max.config'].search(
                [('product_category_id', '=', rec.categ_id.id), ('product_id', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_category and rec.categ_id.id:
                rec.value_config_id = value_config_category.id
                rec.value_config_basis = "Category"

            #  for product
            # find out the min and max days of the product by value and storage
            value_config_product = rec.env['min.max.config'].search(
                [('product_id', '=', rec.id), ('company_id', '=', self.env.company.id)], limit=1)
            if value_config_product and rec.id:
                rec.value_config_id = value_config_product.id
                rec.value_config_basis = "Product"

    def _compute_storage_config_id(self):
        for rec in self:
            rec.storage_config_id = False
            rec.storage_config_basis = None
            # for franchise division
            storage_config_franchise_division = rec.env['min.max.config.storage'].search(
                [('franchise_division', '=', rec.company_type.id), ('product_id', '=', False),
                 ('product_category_id', '=', False), ('product_division', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_franchise_division and rec.company_type.id:
                rec.storage_config_id = storage_config_franchise_division.id
                rec.storage_config_basis = "Franchise Division"

            # for product division
            storage_config_product_division = rec.env['min.max.config.storage'].search(
                [('product_division', '=', rec.product_division_id.id), ('product_id', '=', False),
                 ('product_category_id', '=', False), ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_product_division and rec.product_division_id.id:
                rec.storage_config_id = storage_config_product_division.id
                rec.storage_config_basis = "Product Division"

            # for product category
            storage_config_category = rec.env['min.max.config.storage'].search(
                [('product_category_id', '=', rec.categ_id.id), ('product_id', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_category and rec.categ_id.id:
                rec.storage_config_id = storage_config_category.id
                rec.storage_config_basis = "Category"

            # for product
            storage_config_product = rec.env['min.max.config.storage'].search(
                [('product_id', '=', rec.id), ('company_id', '=', self.env.company.id)], limit=1)
            if storage_config_product and rec.id:
                rec.storage_config_id = storage_config_product.id
                rec.storage_config_basis = "Product"
