# -*- coding: utf-8 -*-
from odoo import models, api, fields
import pandas as pd

class PosSalesReports(models.AbstractModel):
    _name = 'report.pos_product_sale_report.brand_template'
    _description = 'Report POS Sales'


    @api.model
    def _get_report_values(self, docids, data=None):
        # data values are being received from wizard
        data = data['form']
        date_from = fields.Date.from_string(data['date_from'])
        date_to = fields.Date.from_string(data['date_to'])
        brand_ids = (data['product_brand_ids'])

        po_obj = self.env['pos.order'].sudo().search([])
        pos = po_obj.filtered(lambda x: x.date_order.date() >= date_from and x.date_order.date() <= date_to)
        domain = [('order_id', 'in', pos.ids)]

        brands = None
        if brand_ids:
            brands = self.env['product.brand'].search([('id', 'in', brand_ids)])
            domain.append(('product_id.product_brand_id', 'in', brand_ids))
        cols = ['Item Reference', 'Category', 'Product']

        def create_sales_dataframe():
            # Fetch data from pos.order.line model
            order_lines = self.env['pos.order.line'].search(domain)
            # order_lines = self.env['pos.order.line'].search([])

            # Initialize empty dictionary to store product quantities per company
            product_data = {}

            # Process each order line and accumulate quantities per product and company
            for line in order_lines:
                product_name = line.product_id
                company_name = line.company_id.name
                quantity_sold = line.qty

                # Initialize product entry if not present
                if product_name not in product_data:
                    product_data[product_name] = {}

                # Add or update quantity sold for the company under the product
                if company_name in product_data[product_name]:
                    product_data[product_name][company_name] += quantity_sold
                else:
                    product_data[product_name][company_name] = quantity_sold

            # Create DataFrame from the processed data
            df = pd.DataFrame.from_dict(product_data, orient='index')

            # Replace NaN values (products not sold by certain companies) with 0
            df = df.fillna(0)
            return df

        # Create the sales DataFrame
        sales_df = create_sales_dataframe()

        # Display the DataFrame
        datas = []
        for index, row in sales_df.iterrows():
            totals = 0
            avg = 0
            min = 0
            max = 0
            if len(cols) < 4:
                cols.extend(row.to_dict().keys())
            # total_ads = list(row.to_dict().items())
            sections = list(row.to_dict().items())
            for section in sections:
                totals += section[1]
                if min == 0:
                    min = section[1]
                elif section[1] < min:
                    min = section[1]

                if max == 0:
                    max = section[1]
                elif section[1]> max:
                    max = section[1]
            if totals:
                avg = totals/len(list(row.to_dict().items()))

            datas.append({
                'ref': index.default_code,
                'cat': index.categ_id.display_name,
                'product': index.display_name,
                **row.to_dict(),
                'total': totals,
                'avg': avg,
                'max': max,
                'min': min
            })

        cols.append('Total Sales')
        cols.append('Ave. Branch Sales ADS')
        cols.append('Max ADS')
        cols.append('Min ADS')

        return {
            'brands': (',').join(brands.mapped('name')) if brands else None,
            'date_from': date_from,
            'date_to': date_to,
            'cols': cols,
            'report_name': 'Report Name',
            'docs': datas,
            'model': 'branding.filters',
            'company': self.env.company,
        }

        # data_as_list = sales_df.values.tolist()
