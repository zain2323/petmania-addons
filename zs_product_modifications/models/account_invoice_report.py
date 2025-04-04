from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_procurement_type_id = fields.Many2one(
        comodel_name="procurement.type", string="Procurement Type")
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
    product_packing_size_id = fields.Many2one(
        "packing.size", string="Attribute 4")
    product_attribute_1_id = fields.Many2one(
        "attribute.1", string="Sales Contribution Class")
    product_attribute_2_id = fields.Many2one(
        "attribute.2", string="Attribute 2")
    product_attribute_3_id = fields.Many2one(
        "attribute.3", string="Attribute 3")


    @api.model
    def _select(self):
        select_str = super()._select()
        select_str += """, template.product_procurement_type_id as product_procurement_type_id
            , template.product_division_id as product_division_id
            , template.product_vendor_name_id as product_vendor_name_id
            , template.product_life_stage_id as product_life_stage_id
            , template.product_packing_type_id as product_packing_type_id
            , template.product_material_id as product_material_id
            , template.product_packing_size_id as product_packing_size_id
            , template.product_attribute_1_id as product_attribute_1_id
            , template.product_attribute_2_id as product_attribute_2_id
            , template.product_attribute_3_id as product_attribute_3_id
            """
        return select_str

    @api.model
    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += """
        , template.product_procurement_type_id
        , template.product_division_id
        , template.product_vendor_name_id
        , template.product_life_stage_id
        , template.product_packing_type_id
        , template.product_material_id
        , template.product_packing_size_id
        , template.product_attribute_1_id
        , template.product_attribute_2_id
        , template.product_attribute_3_id
        """
        return group_by_str
