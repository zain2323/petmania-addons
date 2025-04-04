from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_type_id = fields.Many2one(
        "product.type", string="Product Nature")
    product_manufacture_id = fields.Many2one(
        "product.manufacture", string="Manufacturer")
    product_formula_id = fields.Many2one(
        "product.formula", string="Generic")
    product_packsize_id = fields.Many2one(
        "product.packsize", string="Product Pack Size")
    product_core_id = fields.Many2one(
        "product.core", string="Core Product")
    product_storage_id = fields.Many2one(
        "product.storage", string="Storage")

    product_procurement_type_id = fields.Many2one(
        "procurement.type", string="Procurement Type")
    product_division_id = fields.Many2one(
        "product.division", string="Product Division")
    product_vendor_name_id = fields.Many2one(
        "vendor.name", string="Vendor Name")
    product_life_stage_id = fields.Many2one(
        "life.stage", string="Life Stage")
    product_packing_type_id = fields.Many2one(
        "packing.type", string="Packing Type")
    product_material_id = fields.Many2one(
        "product.material", string="Product Material")
    product_attribute_1_id = fields.Many2one(
        "attribute.1", string="Sales Contribution Class")
    product_attribute_2_id = fields.Many2one(
        "attribute.2", string="Attribute 2")
    product_attribute_3_id = fields.Many2one(
        "attribute.3", string="Attribute 3")
    product_packing_size_id = fields.Many2one(
        "packing.size", string="Attribute 4")