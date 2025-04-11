from odoo import fields, models, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_warehouse_config(self):
        """Helper method to get the single warehouse config record."""
        config = self.env['warehouse.config'].search([], limit=1)
        if not config:
            _logger.warning("Warehouse Configuration record not found. Proceeding with standard PO confirmation.")
            return None

        if not config.bond_warehouse or not config.company_warehouse:
            raise UserError(_("Warehouse Configuration is incomplete. Please set both Bond and Company warehouses."))

        if config.bond_warehouse_stock_limit < 0 or config.bond_warehouse_stock_limit > 100:
            raise ValidationError(_("Bond Warehouse Stock Limit percentage must be between 0 and 100."))

        return config

    def _get_destination_location_for_specific_warehouse(self, warehouse):
        self.ensure_one()
        return warehouse.in_type_id.default_location_dest_id.id

    def _create_picking(self):
        """
        Override to create two pickings based on warehouse.config,
        replicating standard post-creation steps (confirm, assign, sequence, message).
        """

        # split will only be performed when warehouse is set to bonded
        if not self.picking_type_id.warehouse_id.is_bonded:
            # if not bonded fallback to default method
            return super(PurchaseOrder, self)._create_picking()

        config = self._get_warehouse_config()
        split_required = config and config.bond_warehouse and config.company_warehouse  # Check if split is needed

        if not split_required:
            _logger.info(
                f"No valid split configuration found for PO {self.mapped('name')}. Calling super()._create_picking().")
            return super(PurchaseOrder, self)._create_picking()

        _logger.info(
            f"Warehouse split configuration found. Processing POs {self.mapped('name')} for split picking creation.")

        company_warehouse = config.company_warehouse

        StockPicking = self.env['stock.picking']

        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                company_picking = None
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    company_picking = StockPicking.with_user(SUPERUSER_ID).create({
                        'picking_type_id': company_warehouse.in_type_id.id,
                        'partner_id': self.partner_id.id,
                        'user_id': False,
                        'date': self.date_order,
                        'origin': self.name,
                        'location_dest_id': self._get_destination_location_for_specific_warehouse(company_warehouse),
                        'location_id': self.partner_id.property_stock_supplier.id,
                        'company_id': self.company_id.id,
                    })
                else:
                    picking = pickings[0]

                if company_picking:
                    moves_company = order.order_line._create_stock_moves(company_picking)
                    moves_company.product_uom_qty = int((config.company_warehouse_stock_limit / 100) * moves_company.purchase_line_id.product_uom_qty)
                    moves_company = moves_company.filtered(
                        lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for moves_company in sorted(moves_company, key=lambda move: move.date):
                        seq += 5
                        moves_company.sequence = seq
                    moves_company._action_assign()

                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq

                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                                               values={'self': picking, 'origin': order},
                                               subtype_id=self.env.ref('mail.mt_note').id)
                if company_picking:
                    company_picking.message_post_with_view('mail.message_origin_link',
                                                           values={'self': company_picking, 'origin': order},
                                                           subtype_id=self.env.ref('mail.mt_note').id)
        return True
