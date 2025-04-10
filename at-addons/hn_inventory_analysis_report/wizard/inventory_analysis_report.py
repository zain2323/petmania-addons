from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import io, base64, pytz
from datetime import datetime, time, date, timedelta
from collections import Counter

import logging
_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    xlwt = None

class InventoryAnalysisReportSortedWarehouses(models.TransientModel):
    _name = 'inventory.analysis.report.sorted.warehouses'
    _description = 'Inventory Analysis Report Sorted Warehouses'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Integer')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouses')
    report_id = fields.Many2one('inventory.analysis.report')



class InventoryAnalysisReport(models.TransientModel):
    _name = 'inventory.analysis.report'
    _description = 'Inventory Analysis Report'

    excel_file = fields.Binary(string='Excel File')

    line_ids = fields.One2many('inventory.analysis.report.product.line', 'report_id')
    sorted_warehouse_ids = fields.One2many('inventory.analysis.report.sorted.warehouses', 'report_id')

    # Filter Date Fields
    type = fields.Selection([
        ('annual', 'Annually'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Date')
    ], default='monthly', required=True)
    
    year = fields.Selection(
        [(str(year), str(year)) for year in range(2030, 2010, -1)],
        string='Year', default=str(datetime.now().year)
    )
    
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Month', default=str(datetime.now().month))

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    company_ids = fields.Many2many('res.company', default=lambda self: self._get_default_companies())
    is_data_fetched = fields.Boolean(default=False)

    # Filter Data Fields
    product_brand_ids = fields.Many2many('product.brand', string='Product Brands')
    product_categ_ids = fields.Many2many('product.category', string='Product Categories')
    product_ids = fields.Many2many('product.product', string='Products', domain="['|', ('company_id','in',company_ids), ('company_id','=',False)]")
    scm_category = fields.Selection([
        ('All', 'All'), ('A', 'High Sales (A)'), ('B', 'Medium Sales (B)'),('C', 'Low Sales (C)')
    ], string='SCM Category', default='All', required=True)
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses', domain="['|', ('company_id','in',company_ids), ('company_id','=',False)]")

    # input fields
    min_days = fields.Integer(string='Min. Days')
    max_days = fields.Integer(string='Max. Days')
    avg_weight_of_brand_container = fields.Float('Avg. Weight of Brand Container')


    def _get_default_companies(self):
        return [(6, 0, self.env.context.get('allowed_company_ids', self.env.company.ids))]


    def _get_company_where_clause(self, alias):
        companies = self.env.context.get('allowed_company_ids', self.env.company.ids)
        if len(companies)==1:
            return f'({alias}.company_id = {companies[0]} OR {alias}.company_id IS NULL)'
        else:
            return f'({alias}.company_id IN {tuple(companies)} OR {alias}.company_id IS NULL)'


    def _get_warehouse_where_clause(self, alias, field, use_and=False):
        if (not self.warehouse_ids) or len(self.warehouse_ids)==0:
            return ''
        if len(self.warehouse_ids)==1:
            query = f'{alias}.{field} = {self.warehouse_ids.ids[0]}'
        else:
            query = f'{alias}.{field} IN {tuple(self.warehouse_ids.ids)}'
        if use_and:
            return f'{query} AND'
        return query


    def get_report_data(self):
        
        # formatting start and end dates
        start, end = False, False

        if self.type == 'annual':
            start = date(year=int(self.year), month=1, day=1)
            end = date(year=int(self.year), month=12, day=31)
        
        elif self.type == 'monthly':
            start = date(year=int(self.year), month=int(self.month), day=1)
            (year, month) = (int(self.year)+1, 1) if int(self.month)==12 else (int(self.year), int(self.month)+1)
            end = date(year=int(year), month=int(month), day=1) - timedelta(days=1)

        elif self.type == 'custom':
            if self.start_date > self.end_date:
                raise ValidationError('Start date cannot be greater than end date.')
            start, end = self.start_date, self.end_date
        
        self.start_date, self.end_date = start, end

        # converting start and end dates to UTC
        # user_tz = pytz.timezone(self.env.user.tz)
        # start_time_localized = user_tz.localize(datetime.combine(start, time.min))
        # end_time_localized = user_tz.localize(datetime.combine(end, time.max))

        tz = self.env.user.tz
        if tz == None or tz == False:
            tz = 'Asia/Karachi'
        user_tz = pytz.timezone(tz)
        utc = pytz.timezone('UTC')
        start_time = datetime.combine(start, time.min, tzinfo=utc)
        end_time = datetime.combine(end, time.max, tzinfo=utc)
        
        start_time = start_time.astimezone(user_tz).replace(tzinfo=None)
        end_time = end_time.astimezone(user_tz).replace(tzinfo=None)



        ################################################################################################
        #####################################  PRODUCTS CONDITION  #####################################
        ################################################################################################
        product_query = '''
            SELECT product.id AS id
            FROM product_product product
            JOIN product_template template ON product.product_tmpl_id=template.id

        '''
        # add where clause if filter is selected
        where_clauses = ['product.active=True', self._get_company_where_clause('template')]
        if self.product_brand_ids:
            clause = f'template.product_brand_id = {self.product_brand_ids.id}' if len(self.product_brand_ids)==1 else f'template.product_brand_id IN {tuple(self.product_brand_ids.ids)}'
            where_clauses.append(clause)
        if self.product_categ_ids:
            clause = f'template.categ_id = {self.product_categ_ids.id}' if len(self.product_categ_ids)==1 else f'template.categ_id IN {tuple(self.product_categ_ids.ids)}'
            where_clauses.append(clause)
        if self.product_ids:
            clause = f'product.id = {self.product_ids.id}' if len(self.product_ids)==1 else f'product.id IN {tuple(self.product_ids.ids)}'
            where_clauses.append(clause)

        product_query += 'WHERE ' + ' AND '.join(where_clauses)
        product_query += ' ORDER BY template.name'
        self.env.cr.execute(product_query)
        product_query_res = self.env.cr.dictfetchall()
        product_ids_result = [i['id'] for i in product_query_res]

        if len(product_ids_result) == 0:
            raise UserError('No Products Found !!!')



        ###############################################################################################
        #######################################  QUERY HELPERS  #######################################
        ###############################################################################################
        company_ids = set(self.env.context.get('allowed_company_ids', self.env.company.ids)) or {}
        products = set(product_ids_result) or {}
        warehouses = set(self.warehouse_ids.ids) or {}
        category_ids = {}

        if len(product_ids_result) == 1:
            product_where_clause = f'= {product_ids_result[0]}'
        else:
            product_where_clause = f'IN {tuple(product_ids_result)}'
        

        #################################################################################################
        #######################################  COMPUTING STOCK  #######################################
        #################################################################################################
        stock_query = f'''
            SELECT 
                quant.product_id AS product_id,
                warehouse.id AS warehouse_id,
                SUM(quant.quantity) AS onhand_quantity
            FROM stock_quant quant
            JOIN stock_location loc ON quant.location_id = loc.id
            JOIN stock_warehouse warehouse ON loc.id = warehouse.lot_stock_id
            WHERE
                {self._get_warehouse_where_clause('warehouse', 'id', use_and=True)}
                {self._get_company_where_clause('quant')} AND
                quant.product_id {product_where_clause} AND
                loc.usage = 'internal'
            GROUP BY quant.product_id, warehouse.id
        '''
        self.env.cr.execute(stock_query)
        stock_results = self.env.cr.dictfetchall()

        stock_results_processed = {}
        for result in stock_results:
            if result['product_id'] in stock_results_processed:
                stock_results_processed[result['product_id']][result['warehouse_id']] = result['onhand_quantity']
            else:
                stock_results_processed[result['product_id']] = { result['warehouse_id'] : result['onhand_quantity'] }



        #################################################################################################
        ###################################  COMPUTING OPENING STOCK  ###################################
        #################################################################################################
        incoming_stock_query = f'''
            SELECT
                move.product_id AS product_id,
                warehouse.id AS warehouse_id,
                SUM(move.product_uom_qty) AS incoming
            FROM stock_move move
            JOIN stock_location loc ON move.location_dest_id=loc.id
            JOIN stock_warehouse warehouse ON move.location_dest_id=warehouse.lot_stock_id
            WHERE
                {self._get_warehouse_where_clause('warehouse', 'id', use_and=True)}
                {self._get_company_where_clause('move')} AND
                move.product_id {product_where_clause} AND
                move.date <= '{start_time}' AND
                loc.usage='internal' AND
                move.state = 'done'
            GROUP BY move.product_id, warehouse.id
        '''
        self.env.cr.execute(incoming_stock_query)
        incoming_stock_results = self.env.cr.dictfetchall()

        incoming_stock_results_processed = {}
        for result in incoming_stock_results:
            if result['product_id'] in incoming_stock_results_processed:
                incoming_stock_results_processed[result['product_id']][result['warehouse_id']] = result['incoming']
            else:
                incoming_stock_results_processed[result['product_id']] = { result['warehouse_id'] : result['incoming'] }

        outgoing_stock_query = f'''
            SELECT
                move.product_id AS product_id,
                warehouse.id AS warehouse_id,
                SUM(move.product_uom_qty) AS outgoing,
                COUNT(*)
            FROM stock_move move
            INNER JOIN stock_location loc ON move.location_id=loc.id
            INNER JOIN stock_warehouse warehouse ON move.location_id=warehouse.lot_stock_id
            WHERE
                {self._get_warehouse_where_clause('warehouse', 'id', use_and=True)}
                {self._get_company_where_clause('move')} AND
                move.product_id {product_where_clause} AND
                move.date <= '{start_time}' AND
                loc.usage='internal' AND
                move.state = 'done'
            GROUP BY move.product_id, warehouse.id
        '''
        self.env.cr.execute(outgoing_stock_query)
        outgoing_stock_results = self.env.cr.dictfetchall()

        outgoing_stock_results_processed = {}
        for result in outgoing_stock_results:
            if result['product_id'] in outgoing_stock_results_processed:
                outgoing_stock_results_processed[result['product_id']][result['warehouse_id']] = result['outgoing']
            else:
                outgoing_stock_results_processed[result['product_id']] = { result['warehouse_id'] : result['outgoing'] }

        # opening_stock_query = f'''
        #     SELECT 
        #         quant.product_id AS product_id,
        #         warehouse.id AS warehouse_id,
        #         SUM(quant.quantity) AS onhand_quantity
        #     FROM stock_quant quant
        #     JOIN stock_location loc ON quant.location_id = loc.id
        #     JOIN stock_warehouse warehouse ON loc.id = warehouse.lot_stock_id
        #     WHERE
        #         {self._get_warehouse_where_clause('warehouse', 'id', use_and=True)}
        #         {self._get_company_where_clause('quant')} AND
        #         quant.product_id {product_where_clause} AND
        #         quant.inventory_date <= '{start_time}' AND
        #         loc.usage = 'internal'
        #     GROUP BY quant.product_id, warehouse.id
        # '''
        # self.env.cr.execute(opening_stock_query)
        # opening_stock_results = self.env.cr.dictfetchall()

        # opening_stock_results_processed = {}
        # for result in opening_stock_results:
        #     if result['product_id'] in opening_stock_results_processed:
        #         opening_stock_results_processed[result['product_id']][result['warehouse_id']] = result['onhand_quantity']
        #     else:
        #         opening_stock_results_processed[result['product_id']] = { result['warehouse_id'] : result['onhand_quantity'] }

        
        #################################################################################################
        #######################################  COMPUTING SALES  #######################################
        #################################################################################################
        # sales_query = f'''
        #     SELECT product_id AS product_id, 
        #         warehouse_id AS warehouse_id,
        #         SUM(sales-sales_return) AS total_sales,
        #         SUM(closing) AS onhand_quantity
        #     FROM get_products_movements_for_inventory_ledger('{company_ids}','{products}','{category_ids}','{warehouses}','{start}','{end}')
        #     GROUP BY product_id, warehouse_id
        #     ORDER BY product_id, warehouse_id
        # '''
        sales_query = f'''
            SELECT sol.product_id AS product_id, 
                so.warehouse_id AS warehouse_id,
                SUM(sol.price_subtotal) AS total_sales,
                SUM(sol.product_uom_qty) AS total_sales_qty
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id=so.id
            WHERE 
                sol.product_id {product_where_clause} AND 
                so.state IN ('done', 'sale', 'approval') AND
                {self._get_warehouse_where_clause('so','warehouse_id', use_and=True)}
                so.date_order >= '{start_time}' AND so.date_order <= '{end_time}'
            GROUP BY product_id, warehouse_id
            ORDER BY product_id, warehouse_id
        '''
        self.env.cr.execute(sales_query)
        sales_results = self.env.cr.dictfetchall()

        sales_results_processed = {}
        for result in sales_results:
            if result['product_id'] in sales_results_processed:
                sales_results_processed[result['product_id']][result['warehouse_id']] = (result['total_sales'], result['total_sales_qty'])
            else:
                sales_results_processed[result['product_id']] = { result['warehouse_id'] : (result['total_sales'], result['total_sales_qty']) }
        

        #################################################################################################
        ################################  COMPUTING SALES CATEGORY (ABC) ################################
        #################################################################################################
        abc_categ_query = f"""
            SELECT 
                product_id AS product_id, 
                warehouse_id AS warehouse_id,
                analysis_category AS analysis_category
            FROM get_abc_sales_analysis_data('{company_ids}', '{products}', '{category_ids}', '{warehouses}', '{self.start_date}', '{self.end_date}', 'all')
            GROUP BY product_id, warehouse_id, analysis_category
        """
        
        self.env.cr.execute(abc_categ_query)
        abc_category_results = self.env.cr.dictfetchall()

        abc_category_processed = {}
        for result in abc_category_results:
            if result['product_id'] in abc_category_processed:
                abc_category_processed[result['product_id']][result['warehouse_id']] = result['analysis_category']
            else:
                abc_category_processed[result['product_id']] = { result['warehouse_id'] : result['analysis_category'] }


        ##################################################################################################
        ####################################  Getting Purchase Stages ####################################
        ##################################################################################################
        stage_wise_data_query = f'''
            SELECT 
                line.product_id AS product_id, 
                stage.id AS stage_id, 
                SUM(line.product_qty) AS quantity
            FROM purchase_order_stage stage
            JOIN purchase_order po ON po.stage_id = stage.id 
            JOIN purchase_order_line line ON line.order_id = po.id
            LEFT JOIN stock_move move ON move.purchase_line_id = line.id AND move.state = 'done'
            WHERE 
                stage.active = True AND
                line.product_id {product_where_clause} AND
                move.id IS NULL -- Exclude lines with completed moves
            GROUP BY line.product_id, stage.id
            ORDER BY line.product_id, stage.id
        '''

        self.env.cr.execute(stage_wise_data_query)
        purchase_stage_results = self.env.cr.dictfetchall()

        purchase_stage_processed = {}
        for i in purchase_stage_results:
            if i['product_id'] in purchase_stage_processed:
                purchase_stage_processed[i['product_id']][i['stage_id']] = i['quantity']
            else:
                purchase_stage_processed[i['product_id']] = { i['stage_id'] : i['quantity'] }


        #################################################################################################
        ################################  SORTING ACCORDING TO ABC CATEG ################################
        #################################################################################################

        priority = {"A": 1, "B": 2, "C": 3, "D":3}

        main_data = {}

        for product_id in product_ids_result:
            product_data = []
            grand_total_sales = 0
            
            stock, sales = stock_results_processed.get(product_id, {}), sales_results_processed.get(product_id, {})
            # opening_stock = opening_stock_results_processed.get(product_id, {})
            incoming_stock = incoming_stock_results_processed.get(product_id, {})
            outgoing_stock = outgoing_stock_results_processed.get(product_id, {})
            analysis_category = abc_category_processed.get(product_id, {})
            # if (not stock) and (not sales):
            #     continue
            
            warehouse_ids = set(list(stock.keys()) + list(sales.keys()))

            for warehouse_id in warehouse_ids:
                if self.scm_category=='All' or self.scm_category==analysis_category.get(warehouse_id, False):
                    total_sales, total_sales_qty = sales.get(warehouse_id, (0, 0))
                    grand_total_sales += total_sales
                    product_data.append({
                        'warehouse_id' : warehouse_id,
                        'onhand_quantity' : stock.get(warehouse_id, 0),
                        # 'opening_stock' : opening_stock.get(warehouse_id, 0),
                        'opening_stock' : incoming_stock.get(warehouse_id, 0) - outgoing_stock.get(warehouse_id, 0),
                        'total_sales' : total_sales,
                        'total_sales_qty' : total_sales_qty,
                        'scm_category' : analysis_category.get(warehouse_id, False)
                    })
            
            # if not product_data:
            #     continue

            if product_data:
                product_data = sorted(
                    product_data, 
                    key=lambda x: (priority.get(x['scm_category']) or float('inf'))
                )
                main_data[product_id] = [product_data[0]['scm_category'] or 'D', grand_total_sales] + product_data
            else:
                main_data[product_id] = ['E', grand_total_sales]


        main_data_sorted = dict(sorted(
            main_data.items(), key=lambda item: item[1][1], reverse=True
        ))


        warehouse_sorted = []

        ##################################################################################################
        ########################################  CREATING LINES  ########################################
        ##################################################################################################
        self.line_ids.unlink()
        self.sorted_warehouse_ids.unlink()

        count = 0
        for product_id, warehouse_data in main_data_sorted.items():
            count += 1
            product_line_id = self.env['inventory.analysis.report.product.line'].create({
                'report_id' : self.id,
                'product_id' : product_id,
                'sequence' : count
            })

            if purchase_stage_processed.get(product_id, False):
                for stage, qty in purchase_stage_processed[product_id].items():
                    self.env['inventory.analysis.report.stage.line'].create({
                        'product_line_id' : product_line_id.id,
                        'stage_id' : stage,
                        'quantity' : qty
                    })

            for warehouse in warehouse_data[2:]:
                if not warehouse['warehouse_id']:
                    continue
                if warehouse['warehouse_id'] not in warehouse_sorted:
                    warehouse_sorted.append(warehouse['warehouse_id'])

                warehouse['product_line_id'] = product_line_id.id
                self.env['inventory.analysis.report.warehouse.line'].create(warehouse)
        
        for ind, wh in enumerate(warehouse_sorted):
            self.env['inventory.analysis.report.sorted.warehouses'].create({
                'sequence' : ind+1,
                'warehouse_id' : wh,
                'report_id' : self.id
            })
            

        # returning the wizard action
        self.is_data_fetched = True
        action = self.env.ref('hn_inventory_analysis_report.action_inventory_analysis_report').read()[0]
        action.update({'res_id' : self.id})
        return action
        

    def view_data(self):
        self.ensure_one()
        warehouse_lines_query = f'''
            SELECT whl.id AS id
            FROM inventory_analysis_report_product_line prod_line
            JOIN inventory_analysis_report_warehouse_line whl ON whl.product_line_id=prod_line.id
            WHERE prod_line.report_id={self.id}
        ''' 
        self.env.cr.execute(warehouse_lines_query)
        warehouse_line_ids = self.env.cr.dictfetchall()
        
        action = self.env.ref('hn_inventory_analysis_report.action_inventory_analysis_report_warehouse_line').read()[0]
        action.update({'domain' : [('id','in',[i['id'] for i in warehouse_line_ids])]})
        return action


    def print_excel(self):
        self.ensure_one()
        if not xlwt:
            raise Warning (""" You Don't have xlwt library.\n Please install it by executing this command :  sudo pip3 install xlwt""")
        

        #####################################################################################################
        #############################################  HELPERS  #############################################
        #####################################################################################################
        def format_date(date_value):
            return date_value.strftime('%m-%b-%Y')
        
        def float_to_str(float_value):
            return f"{float_value:,.2f}"
        
        def get_data_style(color=False):
            style = "align: vertical center,horiz center;"
            if color:
                style = f"align: vertical center,horiz center; pattern: pattern solid, fore_colour {color};"
                if color == 'black':
                    style = f"align: vertical center,horiz center; pattern: pattern solid, fore_colour {color}; font: color white;"
            return xlwt.easyxf(style)


        ######################################################################################################
        ##############################################  STYLES  ##############################################
        ######################################################################################################
        style_title = xlwt.easyxf("font:bold on,; align: vertical center,horiz center; border: top thin, bottom thin, right thin, left thin")
        style_title_last_lines = xlwt.easyxf("font:bold on,; align: vertical center,horiz right;")
        data_style = get_data_style()
        colored_styles = {
            'blue': get_data_style('blue'),
            'red': get_data_style('red'),
            'green': get_data_style('green'),
            'black': get_data_style('black'),
            # 'yellow': get_data_style('yellow')
        }
        product_data_style = xlwt.easyxf("align: vertical center;")
        
        ####################################################################################################
        ####################################  WORKBOOK INITITALIZATION  ####################################
        ####################################################################################################
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('ABC ANALYSIS REPORT')

        #####################################################################################################
        ##########################  FILTERING WAREHOUSES AND SEPARATING BONDED WH  ##########################
        #####################################################################################################
        warehouses = self.mapped('sorted_warehouse_ids').sorted(lambda x: x.sequence).mapped('warehouse_id')
        bonded_warehouse = warehouses.filtered(lambda x: x.is_bonded)
        warehouses -= bonded_warehouse

        #####################################################################################################
        ###################################  GETTING ALL PURCHASE STAGES  ###################################
        #####################################################################################################
        purchase_stages_reversed = self.env['purchase.order.stage'].search([])
        purchase_stages = self.env['purchase.order.stage']

        for i in range(len(purchase_stages_reversed)-1, -1, -1):
            purchase_stages |= purchase_stages_reversed[i]
            
        purchase_names_count = Counter([i.name for i in purchase_stages])

        #####################################################################################################
        ##########################################  MAIN HEADINGS  ##########################################
        #####################################################################################################
        row, col = 2, 0
        worksheet.write_merge(row, row+1, col, col, 'PRODUCT BRAND', style=style_title)
        col += 1
        worksheet.write_merge(row, row+1, col, col, 'PRODUCTS', style=style_title)
        col += 1

        for warehouse in warehouses | bonded_warehouse:
            st_col = col
            worksheet.write(row+1, col, 'Category', style=style_title)
            col += 1
            worksheet.write(row+1, col, 'Transit Stock', style=style_title)
            col += 1
            worksheet.write(row+1, col, 'Stock', style=style_title)
            col += 1
            if not warehouse.is_bonded: worksheet.write(row+1, col, 'ADS', style=style_title)
            else: worksheet.write(row+1, col, 'Company ADS', style=style_title)
            col +=1
            worksheet.write(row+1, col, 'Stamina', style=style_title)
            col += 1
            worksheet.write(row+1, col, 'PHI (%)', style=style_title)
            col += 1
            worksheet.write_merge(row, row, st_col, col-1, warehouse.name, style=style_title)


        worksheet.write_merge(row, row+1, col, col, 'COMPANY STOCK', style=style_title)
        col += 1
        worksheet.write_merge(row, row+1, col, col, 'COMPANY ADS', style=style_title)
        col += 1
        worksheet.write_merge(row, row+1, col, col, 'COMPANY STAMINA', style=style_title)
        col += 1

        worksheet.write_merge(row, row+1, col, col, 'WEIGHT', style=style_title)
        col += 1
        worksheet.write_merge(row, row+1, col, col, 'ADSW', style=style_title)
        col += 1

        last_col = col-1
        worksheet.write_merge(0, 1, 0, last_col, 'DETAILED WAREHOUSE WISE REPORT', style=style_title)

        start_col = col
        purchase_stages_sequence = {}       # sequence : list of ids
        exclude_names = []
        count = 0
        for stage in purchase_stages:
            count += 1
            suffix = []
            if purchase_names_count.get(stage.name, 0) == 1:
                if stage.stage_type == 'direct':
                    suffix.append('Direct')
                else:
                    suffix.append('Indirect')
                if stage.consignment_type == 'normal':
                    suffix.append('Normal')
                else:
                    suffix.append('Bulk')
                worksheet.write_merge(row, row+1, col, col, f'''{stage.name} ({' - '.join(suffix)})''', style=style_title)
                col += 1
                purchase_stages_sequence[count] = [stage.id]
            else:
                if stage.name not in exclude_names:
                    exclude_names.append(stage.name)
                    purchase_stages_sequence[count] = purchase_stages.filtered(lambda x: x.name == stage.name).ids
                    worksheet.write_merge(row, row+1, col, col, stage.name, style=style_title)
                    col += 1


        worksheet.write_merge(row, row+1, col, col, 'Total In Transit (Stamina)', style=style_title)
        col += 1
        worksheet.write_merge(row, row+1, col, col, 'GRAND TOTAL', style=style_title)
        col += 1
        worksheet.write_merge(0, 1, start_col, col-1, 'INVENTORY INTRANSIT REPORT', style=style_title)


        ####################################################################################################
        ##############################################  DATA  ##############################################
        ####################################################################################################
        total_product_adsw = 0
        warehouse_wise_color_coding_count = {}

        row += 2
        for line in self.line_ids.sorted(lambda x: x.sequence):
            col=0

            worksheet.write(row, col, line.product_id.product_brand_id.name or '', style=product_data_style)
            col += 1
            worksheet.write(row, col, f'[{line.product_id.default_code}] {line.product_id.name}', style=product_data_style)
            col += 1

            total_stock, total_ads = 0, 0

            # writing warehouses data and totaling stocks and ads
            for warehouse in warehouses:
                stock, transit_stock, ads, stock_per_ads, wh_style = 0, 0, 0, 0, colored_styles['black']
                inv_phi, color_coding = 0, 'black'

                wh = line.warehouse_line_ids.filtered(lambda x: x.warehouse_id==warehouse)
                if wh:
                    stock, ads, stock_per_ads = wh.onhand_quantity, wh.avg_daily_sales, wh.stock_per_ads
                    transit_stock, inv_phi = wh.transit_stock, wh.inventory_phi
                    wh_style = colored_styles[wh.color_coding] if wh.color_coding else colored_styles['black']

                    # maintaining warehouse wise color coding count
                    if wh.color_coding:
                        color_coding = wh.color_coding
                            
                    total_stock, total_ads = total_stock+stock, total_ads+ads

                # maintaining warehouse wise color coding count
                if warehouse.id in warehouse_wise_color_coding_count:
                    if color_coding in warehouse_wise_color_coding_count[warehouse.id]:
                        warehouse_wise_color_coding_count[warehouse.id][color_coding] += 1
                    else:
                        warehouse_wise_color_coding_count[warehouse.id].update({ color_coding : 1 })
                else:
                    warehouse_wise_color_coding_count.update({ warehouse.id : { color_coding : 1 } })

                worksheet.write(row, col, wh.scm_category or '-', style=data_style)
                col += 1
                worksheet.write(row, col, float_to_str(transit_stock), style=data_style)
                col +=1
                worksheet.write(row, col, float_to_str(stock), style=data_style)
                col +=1
                worksheet.write(row, col, float_to_str(ads), style=data_style)
                col +=1
                worksheet.write(row, col, float_to_str(stock_per_ads), style=wh_style)
                col += 1
                worksheet.write(row, col, float_to_str(inv_phi), style=data_style)
                col += 1
            if bonded_warehouse:
                stock, transit_stock, ads, stock_per_ads, wh_style = 0, 0, total_ads, 0, colored_styles['black']
                wh = line.warehouse_line_ids.filtered(lambda x: x.warehouse_id==bonded_warehouse)
                if wh:
                    stock, stock_per_ads = wh.onhand_quantity, ((wh.onhand_quantity/ads) if ads else 0)
                    transit_stock, inv_phi = wh.transit_stock, wh.inventory_phi
                    color_coding = wh._get_color_coding(stock, ads, self.min_days, self.max_days)
                    wh_style = colored_styles[color_coding] if color_coding else colored_styles['black']
                    
                    #color coding count
                    if color_coding:
                        if bonded_warehouse.id in warehouse_wise_color_coding_count:
                            if color_coding in warehouse_wise_color_coding_count[bonded_warehouse.id]:
                                warehouse_wise_color_coding_count[bonded_warehouse.id][color_coding] += 1
                            else:
                                warehouse_wise_color_coding_count[bonded_warehouse.id].update({ color_coding : 1 })
                        else:
                            warehouse_wise_color_coding_count.update({ bonded_warehouse.id : { color_coding : 1 } })

                total_stock += stock

                worksheet.write(row, col, wh.scm_category or '-', style=data_style)
                col += 1
                worksheet.write(row, col, float_to_str(transit_stock), style=data_style)
                col += 1
                worksheet.write(row, col, float_to_str(stock), style=data_style)
                col += 1
                worksheet.write(row, col, float_to_str(ads), style=data_style)
                col += 1
                worksheet.write(row, col, float_to_str(stock_per_ads), style=wh_style)
                col += 1
                worksheet.write(row, col, float_to_str(inv_phi), style=data_style)
                col += 1

            # after writing warehouses data, write product line columns data
            worksheet.write(row, col, float_to_str(line.total_stock), style=data_style)
            col += 1
            worksheet.write(row, col, float_to_str(total_ads), style=data_style)
            col += 1
            worksheet.write(row, col, float_to_str(line.company_stamina), style=data_style)
            col += 1
            worksheet.write(row, col, float_to_str(line.product_id.weight), style=data_style)
            col += 1

            product_adsw = line._get_adsw(line.product_id.weight, total_ads)
            total_product_adsw += product_adsw
            worksheet.write(row, col, float_to_str(product_adsw), style=data_style)
            col += 1

            # writing purchases
            total_qty = 0
            for i, j in purchase_stages_sequence.items():
                records = line.stage_line_ids.filtered(lambda x: x.stage_id.id in j)
                qty = 0
                if records:
                    qty = sum([rec.quantity for rec in records])
                    total_qty += qty
                worksheet.write(row, col, float_to_str(qty), style=data_style)
                col += 1
                
            total_intransit_stamina = total_qty / total_ads if total_ads else 0
            worksheet.write(row, col, float_to_str(total_intransit_stamina), style=data_style)
            col += 1
            worksheet.write(row, col, float_to_str(total_intransit_stamina + line.company_stamina), style=data_style)
            col += 1

            # one product has been written so changing the row for the next one
            row += 1
        
        # all products have been written, write the count of each warehouses now
        row += 1
        col = 1
        
        # colors_lst = ['green', 'blue','red','black','yellow']
        colors_lst = ['green', 'blue','red','black']
        worksheet.write(row, col, 'Ideal Stock', style=data_style)
        worksheet.write(row+1, col, 'Under Stock', style=data_style)
        worksheet.write(row+2, col, 'Over Stock', style=data_style)
        worksheet.write(row+3, col, 'Out of Stock', style=data_style)
        worksheet.write(row+4, col, 'Non-Moving Stock', style=data_style)
        col += 1
        reset_col = col
        
        for color in colors_lst:
            for warehouse in warehouses:
                col += 4
                amt = warehouse_wise_color_coding_count.get(warehouse.id, {}).get(color, 0)
                worksheet.write(row, col, amt, style=data_style)
                col += 2
            
            if bonded_warehouse:
                col += 4
                amt = warehouse_wise_color_coding_count.get(bonded_warehouse.id, {}).get(color, 0)
                worksheet.write(row, col, amt, style=data_style)
                col += 2

            row += 1
            col = reset_col
        
        
        #####################################################################################################
        ###########################################  FOOTER DATA  ###########################################
        #####################################################################################################
        row, col= row+1, last_col-3
        input_adsw = self.avg_weight_of_brand_container or 0

        worksheet.write_merge(row, row, col, col+2, 'Brand ADSW', style=style_title_last_lines)
        worksheet.write(row, col+3, float_to_str(total_product_adsw), style=data_style)
        row +=1

        worksheet.write_merge(row, row, col, col+2, 'Average Container Weight', style=style_title_last_lines)
        worksheet.write(row, col+3, float_to_str(input_adsw), style=data_style)
        row += 1

        worksheet.write_merge(row, row, col, col+2, 'Daily Container Consumption', style=style_title_last_lines)
        worksheet.write(row, col+3, float_to_str((total_product_adsw/input_adsw)*100 if input_adsw else 0), style=data_style)
        row += 1

        worksheet.write_merge(row, row, col, col+2, 'Container Consumption Day', style=style_title_last_lines)
        worksheet.write(row, col+3, float_to_str(input_adsw/total_product_adsw if total_product_adsw else 0), style=data_style)
        row += 1

        #####################################################################################################
        ##############################  STORING DATA AND RETURNING URL ACTION  ##############################
        #####################################################################################################
        filename = f'INVENTORY ANALYSIS REPORT.xls'
        field_name = 'excel_file'

        fp = io.BytesIO()
        workbook.save(fp)
        self.write({field_name : base64.b64encode(fp.getvalue())})
        fp.close()

        return {
            'type': 'ir.actions.act_url',
            'name': "Inventory Analysis Report",
            'url': f"/web/content/{self._name}/{self.id}/{field_name}/{filename}?download=true",
            'target' : 'self'
        }
