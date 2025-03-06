from odoo import api, fields, models


class ProductType(models.Model):
    _name = "product.type"
    _description = "Product Type"

    name = fields.Char("Product Nature", required=True)

class ProductManfacture(models.Model):
    _name = "product.manufacture"
    _description = "Product Manufacture"

    name = fields.Char("Manufacturer", required=True)

class ProductFormula(models.Model):
    _name = "product.formula"
    _description = "Product Formula"

    name = fields.Char("Formula", required=True)

class ProductPackSize(models.Model):
    _name = "product.packsize"
    _description = "Product Pack Size"

    name = fields.Char("Packing Size", required=True)

class ProductCore(models.Model):
    _name = "product.core"
    _description = "Product Core"

    name = fields.Char("Core Product", required=True)


class ProductStorage(models.Model):
    _name = "product.storage"
    _description = "Product Storage"

    name = fields.Char("Storage", required=True)

class ProcurementType(models.Model):
    _name = "procurement.type"
    _description = "Procurement Type"

    name = fields.Char("Procurement Type", required=True)

class ProductDivision(models.Model):
    _name = "product.division"
    _description = "Product Division"

    name = fields.Char("Product Division", required=True)

class VendorName(models.Model):
    _name = "vendor.name"
    _description = "Vendor Name"

    name = fields.Char("Vendor Name", required=True)

class LifeStage(models.Model):
    _name = "life.stage"
    _description = "Life Stage"

    name = fields.Char("Life Stage", required=True)

class PackingType(models.Model):
    _name = "packing.type"
    _description = "Packing Type"

    name = fields.Char("Packing Type", required=True)

class ProductMaterial(models.Model):
    _name = "product.material"
    _description = "Product Material"

    name = fields.Char("Product Material", required=True)

class PackingNature(models.Model):
    _name = "packing.nature"
    _description = "Packing Nature"

    name = fields.Char("Packing Nature", required=True)

class Attribute1(models.Model):
    _name = "attribute.1"
    _description = "Attribute 1"

    name = fields.Char("Sales Contribution Class", required=True)

class Attribute2(models.Model):
    _name = "attribute.2"
    _description = "Attribute 2"

    name = fields.Char("Pcs in a pallet", required=True)

class Attribute3(models.Model):
    _name = "attribute.3"
    _description = "Attribute 3"

    name = fields.Char("Pcs in a layer/tray", required=True)