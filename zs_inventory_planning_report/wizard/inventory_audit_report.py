from odoo import fields, models, api, _

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from odoo.addons.zs_customer_sales_analysis_report.library import xlsxwriter
import logging

_logger = logging.getLogger(__name__)


class InventoryAuditData(models.Model):
    _name = 'inventory.audit.data'
    _description = 'Inventory Audit Data'

    name = fields.Char(string='Name')
    state = fields.Selection([
        ('draft', 'Draft'), ('start_audit', 'Start Audit'), ('submit', 'Submitted'), ('confirm', 'Confirmed')
    ], string='state', default='draft', required=True)
    assignee_id = fields.Many2one('res.users', string='Assignee', required=False)
    scm_officer_id = fields.Many2one('res.users', string='SCM Officer', required=False)
    line_ids = fields.One2many("inventory.audit.line", "audit_id", string="Audit Lines")
    audit_line_count = fields.Integer(string="Audit Line Count", compute="_compute_audit_line_count")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('audit_report_sequence')
        return super(InventoryAuditData, self).create(vals)

    def _compute_audit_line_count(self):
        for record in self:
            record.audit_line_count = len(record.line_ids)

    def action_open_audit_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Audit Lines',
            'res_model': 'inventory.audit.line',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('zs_inventory_planning_report.view_audit_line_tree').id, 'tree')],
            'domain': [('audit_id', '=', self.id)],
            'context': {'default_audit_id': self.id},
            'target': 'current',
        }

    def _adjust_inventory(self):
        for rec in self:
            for line in rec['line_ids']:
                if line.difference != 0:
                    quant = self.env['stock.quant'].with_context(inventory_mode=True).search(
                        [('product_id', '=', line.product_id.id), ('location_id.usage', '=', 'internal')])
                    if quant:
                        quant['inventory_quantity'] = line.product_id.qty_available + line.difference
                        quant._compute_inventory_quantity_set()
                        quant._compute_inventory_diff_quantity()
                        quant.action_apply_inventory()

    def start_audit(self):
        self.state = 'start_audit'
        self.freeze_products()

    def submit_audit(self):
        self.state = 'submit'
        self.unfreeze_products()

    def finish_audit(self):
        self.state = 'confirm'
        self.unfreeze_products()

    def freeze_products(self):
        lines = self.line_ids
        for line in lines:
            product = self.env['product.product'].search([('id', '=', line.product_id.id)])
            product.available_in_pos_company = False

    def unfreeze_products(self):
        lines = self.line_ids
        for line in lines:
            product = self.env['product.product'].search([('id', '=', line.product_id.id)])
            product.available_in_pos_company = True

    def unlink(self):
        self.unfreeze_products()
        for record in self:
            record.line_ids.unlink()
        return super(InventoryAuditData, self).unlink()


class AuditLines(models.Model):
    _name = 'inventory.audit.line'
    _description = 'Inventory Audit Data Line'

    serial_no = fields.Integer(string='Serial No')
    audit_id = fields.Many2one('inventory.audit.data', string='Audit Data', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    franchise_name = fields.Char(string='Franchise Name')
    division_name = fields.Char(string='Division Name')
    category_name = fields.Char(string='Category Name')
    brand_name = fields.Char(string='Brand Name')
    product_name = fields.Char(string='Product Name')
    barcode = fields.Char(string='Barcode')
    qty_available = fields.Integer(string='System Count')
    counted_qty = fields.Integer(string='Physical Count')
    difference = fields.Integer(string='QTY Difference', compute='_compute_difference', store=True)
    remarks = fields.Char(string='Remarks')
    status = fields.Char(string='Status')

    @api.depends("qty_available", "counted_qty")
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.counted_qty - rec.qty_available
            if rec.difference < 0:
                rec.status = 'deficient'
            elif rec.difference > 0:
                rec.status = 'surplus'
            else:
                rec.status = 'ideal'

    def unfreeze_products(self):
        for rec in self:
            rec.product_id.available_in_pos_company = True

    def _adjust_inventory(self):
        for line in self:
            if line.difference != 0:
                quant = self.env['stock.quant'].with_context(inventory_mode=True).search(
                    [('product_id', '=', line.product_id.id), ('location_id.usage', '=', 'internal')])
                if quant:
                    quant['inventory_quantity'] = line.product_id.qty_available + line.difference
                    quant._compute_inventory_quantity_set()
                    quant._compute_inventory_diff_quantity()
                    quant.action_apply_inventory()


class CustomerWiseSalesAnalysisReport(models.TransientModel):
    _name = 'inventory.audit.report.wizard'

    file_data = fields.Binary('File Data')
    franchise_division_ids = fields.Many2many('product.company.type', string="Franchise Division")
    product_division_ids = fields.Many2many('product.division', string="Product Division")
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_ids = fields.Many2many('product.product', string='Products')

    def action_view_pivot(self):
        record = self.populate_pivot_data()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Audit Report',
            'res_model': 'inventory.audit.data',
            'view_mode': 'form',
            'target': 'current',
            'res_id': record.id,
        }

    def _get_data_for_products(self):
        domain = [('available_in_pos_company', '=', True)]

        if self.franchise_division_ids:
            domain.append(('company_type', 'in', self.franchise_division_ids.ids))

        if self.product_division_ids:
            domain.append(('product_division_id', 'in', self.product_division_ids.ids))

        if self.product_category_ids:
            domain.append(('categ_id', 'in', self.product_category_ids.ids))

        if self.product_brand_ids:
            domain.append(('product_brand_id', 'in', self.product_brand_ids.ids))

        if self.product_ids:
            domain.append(('id', 'in', self.product_ids.ids))

        products = self.env['product.product'].search(domain)
        products_dict = []
        for product in products:
            products_dict.append({
                'product_id': product.id,
                'product_name': product.name,
                'brand_name': product.product_brand_id.name,
                'category_name': product.categ_id.name,
                'franchise_name': product.company_type.name,
                'division_name': product.product_division_id.name,
                'barcode': product.barcode,
                'qty_available': product.qty_available,
                'counted_qty': None,
                'difference': 0,
                'remarks': "",
            })
        return products_dict

    def populate_pivot_data(self):
        products_data = self._get_data_for_products()
        inventory_data = self.env['inventory.audit.data'].create({
            "scm_officer_id": self.env.user.id,
            'name': f"{self.env.company.name}-Audit-{self.id}",
        })
        serial_no = 1
        for product_data in products_data:
            self.env['inventory.audit.line'].create({
                'serial_no': serial_no,
                'product_id': product_data['product_id'],
                'audit_id': inventory_data.id,
                'product_name': product_data['product_name'],
                'franchise_name': product_data['franchise_name'],
                'division_name': product_data['division_name'],
                'category_name': product_data['category_name'],
                'brand_name': product_data['brand_name'],
                'barcode': product_data['barcode'],
                'qty_available': product_data['qty_available'],
                'counted_qty': product_data['counted_qty'],
                'difference': product_data['difference'],
                'remarks': product_data['remarks'],
            })
            serial_no += 1
        return inventory_data
