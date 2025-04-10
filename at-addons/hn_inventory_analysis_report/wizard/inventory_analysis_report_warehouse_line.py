from odoo import fields, models, api, _
import pytz
from datetime import timedelta, datetime, time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class InventoryAnalysisReportWarehouseLine(models.TransientModel):
    _name = 'inventory.analysis.report.warehouse.line'
    _description = 'Inventory Analysis Report Warehouse Lines'

    product_line_id = fields.Many2one('inventory.analysis.report.product.line')
    start_date = fields.Date(related='product_line_id.start_date', store=True)
    end_date = fields.Date(related='product_line_id.end_date', store=True)
    product_id = fields.Many2one(related='product_line_id.product_id', store=True)
    product_brand = fields.Many2one(related='product_id.product_brand_id', store=True)

    weight = fields.Float(related='product_id.weight', store=True)

    scm_category = fields.Selection([('A','A'), ('B','B'), ('C','C')], string='SCM category')

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    transit_stock = fields.Float(string='Transit Stock', compute='_compute_transit_stock', store=True)
    onhand_quantity = fields.Float(string='Stock')
    total_sales = fields.Float(string='Total Sales')
    total_sales_qty = fields.Float(string='Total Sales Qty')

    avg_daily_sales = fields.Float(string='ADS', compute='_compute_avg_daily_sales', store=True)
    total_ads = fields.Float(related='product_line_id.total_ads')

    stock_per_ads = fields.Float(string='Stamina', compute='_compute_stock_per_ads', store=True)
    color_coding = fields.Selection([
        ('blue','Blue'), ('red','Red'),
        ('green', 'Green'), ('black','Black'),
        ('yellow','Yellow')
    ], string='Color', compute='_compute_color_coding')

    opening_stock = fields.Float(string='Opening Stock')
    inventory_phi = fields.Float(string='PHI', compute='_compute_inventory_phi', store=True)


    @api.depends('warehouse_id', 'product_id')
    def _compute_transit_stock(self):
        # all_transits = self.env['stock.location'].search([('name', 'ilike', 'transit')])
        for rec in self:
            rec.transit_stock = False
            if not (rec.warehouse_id and rec.product_id):
                continue
            
            # transit_loc = all_transits.filtered(lambda x: rec.warehouse_id.lot_stock_id.display_name in x.display_name)
            transit_loc = self.env['stock.location'].search([('parent_warehouse', '=', rec.warehouse_id.id), ('usage','=','transit')])
            if not transit_loc:
                continue
            
            transit_loc = transit_loc if len(transit_loc)==1 else transit_loc[0]
            company_clause = self.product_line_id.report_id._get_company_where_clause('quant')
            self.env.cr.execute(f"""
                SELECT SUM(quant.quantity) AS stock
                FROM stock_quant quant
                WHERE
                    quant.location_id = {transit_loc.id} AND
                    {company_clause} AND
                    quant.product_id={rec.product_id.id}
            """)
            results = self.env.cr.dictfetchone()
            rec.transit_stock = results.get('stock')


    @api.depends('warehouse_id', 'product_id', 'opening_stock')
    def _compute_inventory_phi(self):
        for rec in self:
            if not (rec.warehouse_id and rec.product_id):
                rec.inventory_phi = 0
                continue

            tz = self.env.user.tz
            if tz == None or tz == False:
                tz = 'Asia/Karachi'
            user_tz = pytz.timezone(tz)
            utc = pytz.timezone('UTC')
            start_time = datetime.combine(rec.start_date, time.min, tzinfo=utc)
            end_time = datetime.combine(rec.end_date, time.max, tzinfo=utc)
            
            start_time = start_time.astimezone(user_tz).replace(tzinfo=None)
            end_time = end_time.astimezone(user_tz).replace(tzinfo=None)


            stock, date, loc = rec.opening_stock, start_time, rec.warehouse_id.lot_stock_id
            moves = self.env['stock.move'].search([('state','=','done'), ('date', '>=', start_time), ('date', '<=', end_time), ('product_id','=',rec.product_id.id),
                                                   '|', ('location_id', '=', loc.id), ('location_dest_id', '=', loc.id)])
            in_stock = 0
            while date <= end_time:
                prev_date = date
                date += timedelta(days=1)
                for i in moves.filtered(lambda x: prev_date <= x.date <= date):
                    if i.location_dest_id.id == loc.id:
                        stock += i.product_uom_qty
                    if i.location_id.id == loc.id:
                        stock -= i.product_uom_qty

                if stock > 0:
                    in_stock += 1
            
            no_of_days = self._get_days_between_dates(rec.start_date, rec.end_date)
            rec.inventory_phi = (in_stock / no_of_days) * 100
            


    @api.depends('start_date', 'end_date', 'total_sales_qty', 'total_ads', 'warehouse_id')
    def _compute_avg_daily_sales(self):
        for rec in self:
            if rec.warehouse_id.is_bonded:
                rec.avg_daily_sales = rec.total_ads
            else:
                rec.avg_daily_sales = self._get_avg_daily_sales(rec.start_date, rec.end_date, rec.total_sales_qty)


    @api.depends('onhand_quantity','avg_daily_sales', 'product_line_id.report_id.min_days', 'product_line_id.report_id.max_days')
    def _compute_color_coding(self):
        for rec in self:
            min_days = rec.product_line_id.report_id.min_days or 0
            max_days = rec.product_line_id.report_id.max_days or 0
            rec.color_coding = self._get_color_coding(rec.onhand_quantity, rec.avg_daily_sales, min_days, max_days)


    @api.depends('onhand_quantity', 'avg_daily_sales')
    def _compute_stock_per_ads(self):
        for rec in self:
            rec.stock_per_ads = rec.onhand_quantity / rec.avg_daily_sales if rec.avg_daily_sales else 0


    def _get_avg_daily_sales(self, start_date, end_date, total_sales):
        return total_sales / self._get_days_between_dates(start_date, end_date)


    def _get_forecasted_qty(self, start_date, end_date, onhand_quantity):
        return onhand_quantity / self._get_days_between_dates(start_date, end_date)


    def _get_color_coding(self, stock, ads, min_days, max_days):
        stock_held = round(stock / ads) if round(ads, 2) else 0

        # if stock > 0 and ads == 0:
        #     return 'yellow'
        if round(stock, 2) == 0 or stock_held == 0:
            return 'black'
        if min_days <= stock_held <= max_days:
            return 'green'
        if stock_held > max_days:
            return 'red'
        if stock_held < min_days:
            return 'blue'
        
        return False
    

    def _get_days_between_dates(self, start, end):
        date_difference = end-start
        if isinstance(date_difference, timedelta):
            return date_difference.days + 1
        else:
            return date_difference + 1

