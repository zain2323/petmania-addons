from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

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
        "attribute.2", string="Pcs in a pallet")
    product_attribute_3_id = fields.Many2one(
        "attribute.3", string="Pcs in a layer")
    product_packing_nature_id = fields.Many2one(
        "packing.nature", string="Packing Nature")
    product_packsize_id = fields.Many2one(
        "product.packsize", string="Packing Size")
    product_pcs_in_a_tray = fields.Many2one(
        "pcs.tray", string="Pcs in a try")

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """
        , t.product_procurement_type_id
        , t.product_division_id
        , t.product_vendor_name_id
        , t.product_life_stage_id
        , t.product_packing_type_id
        , t.product_material_id
        , t.product_packing_nature_id
        , t.product_attribute_1_id
        , t.product_attribute_2_id
        , t.product_attribute_3_id
        , t.product_packsize_id
        , t.product_pcs_in_a_tray
        """
        return res

    def _select_additional_fields(self, fields):
        fields["product_procurement_type_id"] = ", t.product_procurement_type_id as product_procurement_type_id"
        fields["product_division_id"] = ", t.product_division_id as product_division_id"
        fields["product_vendor_name_id"] = ", t.product_vendor_name_id as product_vendor_name_id"
        fields["product_life_stage_id"] = ", t.product_life_stage_id as product_life_stage_id"
        fields["product_packing_type_id"] = ", t.product_packing_type_id as product_packing_type_id"
        fields["product_material_id"] = ", t.product_material_id as product_material_id"
        fields["product_packing_nature_id"] = ", t.product_packing_nature_id as product_packing_nature_id"
        fields["product_attribute_1_id"] = ", t.product_attribute_1_id as product_attribute_1_id"
        fields["product_attribute_2_id"] = ", t.product_attribute_2_id as product_attribute_2_id"
        fields["product_attribute_3_id"] = ", t.product_attribute_3_id as product_attribute_3_id"
        fields["product_packsize_id"] = ", t.product_packsize_id as product_packsize_id"
        fields["product_pcs_in_a_tray"] = ", t.product_pcs_in_a_tray as product_pcs_in_a_tray"
        return super()._select_additional_fields(fields)
