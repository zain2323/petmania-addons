# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Customer Sales Analysis Report',
    'version' : '15.0.0.2',
    'author' : 'Zain Siddiqui',
    'license' : 'OPL-1',
    'sequence': 25,
    'depends' : ['sale_stock', 'sale', 'customer_ext'],
    'data' : [
        'security/ir.model.access.csv',
        'views/customer_wise_sales_analysis_view.xml',
        'views/customer_sales_analysis_pivot_view.xml',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
}
