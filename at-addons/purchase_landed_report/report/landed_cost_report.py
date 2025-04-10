# -*- coding:utf-8 -*-
from odoo import api, models, fields
from datetime import datetime
import os
from xlsxwriter.utility import xl_rowcol_to_cell


dirname = os.path.dirname(__file__)


class LandedCostXlsx(models.AbstractModel):
    _name = 'report.purchase_landed_report.landed_cost_template'
    _description = 'Vat Sales Xlsx Reports'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard_data):
        # Basic Info
        date_from = wizard_data.date_from
        date_to = wizard_data.date_to
        partner_id = wizard_data.partner_id
        product_id = wizard_data.product_id
        product_categ_id = wizard_data.product_categ_id
        product_brand_id = wizard_data.product_brand_id
        company_id = wizard_data.company_id
        purchase_order_id = wizard_data.purchase_order_id

        worksheet = workbook.add_worksheet('Vat Sales xls')

        worksheet.set_column('A:V', 20)
        worksheet.set_row(0, 30)



        invoice_line_records = self.env['account.move.line'].search([('move_id.invoice_date', '>=', date_from),
                                                                     ('move_id.invoice_date', '<=', date_to),
                                                                     ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
                                                                     ('tax_ids', '!=', False)])
        bill_line_records = self.env['account.move.line'].search([('move_id.invoice_date', '>=', date_from),
                                                                  ('move_id.invoice_date', '<=', date_to),
                                                                  ('move_id.move_type', 'in',
                                                                   ['in_invoice', 'in_refund']),
                                                                  ('tax_ids', '!=', False)])
        # expense_line_records = self.env['hr.expense'].search([('sheet_id.accounting_date', '>=', date_from),
        #                                                       ('sheet_id.accounting_date', '<=', date_to),
        #                                                       ('sheet_id.state', '=', 'post'),
        #                                                       ('tax_ids', '!=', False)])
        # # petty_cash_expense_line_records = self.env['expense.accounting.petty.tree'].search([('expense_accounting_id.date','>=', date_from),
        #                                                                                     ('expense_accounting_id.date', '<=', date_to),
        #                                                                                     ('tax_id', '!=', False)]).sorted(lambda x: x.expense_accounting_id.date, reverse=False)

        header_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            "font_size": '9',
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFFFFF',
            "bg_color": "#333f50"

        })
        data_string_left = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '11',
        })
        data_string_center = workbook.add_format({
            "align": 'center',
            "valign": 'vcenter',
            'font_size': '11',
        })
        data_amount = workbook.add_format({
            "align": 'right',
            "valign": 'vcenter',
            'font_size': '11',
            "num_format": "#,##0.00",
        })

        rows = 0

        worksheet.merge_range(rows, 2, rows, 6,  'Purchase Register Format', header_format)
        worksheet.write(rows + 1, 2, 'Start Date', header_format)
        worksheet.write(rows + 1, 3, str(date_from), data_string_center)
        worksheet.write(rows + 2, 2, 'End Date', header_format)
        worksheet.write(rows + 2, 3, str(date_to), data_string_center)
        worksheet.write(rows + 3, 2, 'Vendor Name', header_format)
        worksheet.write(rows + 3, 3, partner_id.name if partner_id else "", data_string_center)
        worksheet.write(rows + 4, 2, 'Purchase', header_format)
        worksheet.write(rows + 4, 3, purchase_order_id.name if purchase_order_id else "", data_string_center)

        worksheet.write(rows + 1, 5, 'Product Category', header_format)
        worksheet.write(rows + 1, 6, product_categ_id.name if product_categ_id else "", data_string_center)
        worksheet.write(rows + 2, 5, 'Product Name', header_format)
        worksheet.write(rows + 2, 6, product_id.name if product_id else "", data_string_center)
        worksheet.write(rows + 3, 5, 'Brand', header_format)
        worksheet.write(rows + 3, 6, product_brand_id.name if product_brand_id else '', data_string_center)
        worksheet.write(rows + 4, 5, 'Company', header_format)
        worksheet.write(rows + 4, 6, company_id.name, data_string_center)

        rows = rows + 5
        worksheet.write(rows, 0, 'Bill Date', header_format)
        worksheet.write(rows, 1, 'Supplier Name', header_format)
        worksheet.write(rows, 2, 'LC Number', header_format)
        worksheet.write(rows, 3, 'LC Bill Date', header_format)
        worksheet.write(rows, 4, 'PO Number', header_format)
        worksheet.write(rows, 5, 'PO Date', header_format)
        worksheet.write(rows, 6, 'GRN Number', header_format)
        worksheet.write(rows, 7, 'Item Name', header_format)
        worksheet.write(rows, 8, 'Item Category', header_format)
        worksheet.write(rows, 9, 'Item Brand', header_format)
        worksheet.write(rows, 10, 'UOM', header_format)
        worksheet.write(rows, 11, 'PO Price', header_format)
        worksheet.write(rows, 12, 'PO Price in Foreign Currency', header_format)
        worksheet.write(rows, 13, 'Currency Name', header_format)
        worksheet.write(rows, 14, 'Qty', header_format)
        worksheet.write(rows, 15, 'PO Total Value In Foreign Currency', header_format)
        worksheet.write(rows, 16, 'Exchange Rate', header_format)
        worksheet.write(rows, 17, 'Total PO Amount by Product', header_format)
        worksheet.write(rows, 18, 'Total Landed Cost Amount', header_format)
        worksheet.write(rows, 19, 'Product Wise Landed Cost', header_format)
        worksheet.write(rows, 20, 'Item Cost', header_format)
        worksheet.write(rows, 21, 'Total Value', header_format)
        rows = rows + 1
        domain = [('date_approve','>=',date_from),('date_approve','<=',date_to),('company_id','=',company_id.id), ('state', 'in', ['purchase','done'])]
        if partner_id:
            domain.append(
                ('partner_id','=',partner_id.id)
            )
        if purchase_order_id:
            domain.append(
                ('id', '=', purchase_order_id.id)
            )
        po_ids = self.env['purchase.order'].search(domain)
        print(po_ids)
        po_lines = False
        for po in po_ids:
            line_domain = [('order_id','=',po.id)]
            if product_id:
                line_domain.append(('product_id','=',product_id.id))
            if product_categ_id:
                line_domain.append(('product_id.categ_id','=',product_categ_id.id))
            if product_brand_id:
                line_domain.append(('product_id.product_brand_id','=',product_brand_id.id))
            print(line_domain)
            po_lines = self.env['purchase.order.line'].search(line_domain)

            print(po_lines)
            data = []
            if po_lines:
                for line in po_lines:
                    stock_move = self.env['stock.move'].search([('purchase_line_id', '=', line.id), ('state', '=', 'done')], limit=1)
                    valuation = self.env['stock.valuation.adjustment.lines'].search([('move_id', '=', stock_move.id)],limit=1)
                    landed_cost_ids = self.env['stock.valuation.adjustment.lines'].search([('move_id', '=', stock_move.id)])
                    move_line = self.env['account.move.line'].search([('purchase_line_id', '=', line.id)], limit=1)
                    landed_cost = 0
                    for i in landed_cost_ids:
                        landed_cost = landed_cost + i.additional_landed_cost
                    if landed_cost:
                        vals = {
                            'po_line': line,
                            'stock_move': stock_move,
                            'valuation': valuation,
                            'move_line': move_line,
                            'landed_cost': landed_cost,
                        }
                        data.append(vals)
                    # data['po_line'] = line
                    # data['stock_move'] = stock_move

                print(data)
            if data:
                for data_line in data:
                    worksheet.write(rows, 0, str(data_line['move_line'].move_id.invoice_date if data_line['move_line'].move_id.invoice_date else ''), data_string_center)
                    worksheet.write(rows, 1, data_line['po_line'].partner_id.name if data_line['po_line'].partner_id.name else '', data_string_center)
                    worksheet.write(rows, 2, data_line['valuation'].cost_id.name if data_line['valuation'].cost_id else '', data_string_center)
                    worksheet.write(rows, 3, str(data_line['valuation'].cost_id.date if data_line['valuation'].cost_id else ''), data_string_left)
                    worksheet.write(rows, 4, data_line['po_line'].order_id.name if data_line['po_line'].order_id else '', data_string_left)
                    worksheet.write(rows, 5, str(data_line['po_line'].order_id.date_approve.date()), data_string_left)
                    worksheet.write(rows, 6, data_line['stock_move'].picking_id.name, data_string_left)
                    worksheet.write(rows, 7, data_line['po_line'].product_id.name, data_string_left)
                    worksheet.write(rows, 8, data_line['po_line'].product_id.categ_id.name, data_string_left)
                    worksheet.write(rows, 9, data_line['po_line'].product_id.product_brand_id.name if data_line['po_line'].product_id.product_brand_id else '', data_string_left)
                    worksheet.write(rows, 10, data_line['po_line'].product_id.uom_id.name, data_string_left)
                    worksheet.write(rows, 11, data_line['move_line'].unit_price_company_curr, data_string_left)
                    worksheet.write(rows, 12, data_line['po_line'].price_unit, data_string_left)
                    worksheet.write(rows, 13, data_line['po_line'].currency_id.name, data_string_left)
                    worksheet.write(rows, 14, data_line['po_line'].qty_received, data_string_left)
                    worksheet.write(rows, 15, data_line['po_line'].qty_received * data_line['po_line'].price_unit, data_string_left)
                    worksheet.write(rows, 16, data_line['move_line'].exchange_rate, data_string_left)
                    worksheet.write(rows, 17, data_line['move_line'].unit_price_company_curr * data_line['po_line'].qty_received, data_string_left)
                    worksheet.write(rows, 18, data_line['landed_cost'], data_string_left)
                    if data_line['po_line'].qty_received > 0:
                        worksheet.write(rows, 19, '{0:,.4f}'.format(data_line['landed_cost']/data_line['po_line'].qty_received), data_string_left)
                        worksheet.write(rows, 20, '{0:,.4f}'.format((data_line['landed_cost']/data_line['po_line'].qty_received) + data_line['move_line'].unit_price_company_curr), data_string_left)
                        worksheet.write(rows, 21, '{0:,.4f}'.format(data_line['po_line'].qty_received * ((data_line['landed_cost']/data_line['po_line'].qty_received) + data_line['move_line'].unit_price_company_curr)), data_string_left)
                    else:
                        worksheet.write(rows, 19,
                                        '{0:,.4f}'.format(0),
                                        data_string_left)
                        worksheet.write(rows, 20, '{0:,.4f}'.format(0), data_string_left)
                        worksheet.write(rows, 21, '{0:,.4f}'.format(0), data_string_left)

                    rows += 1
