# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sales Analysis Report',
    'version' : '15.0.0.3',
    'author' : 'Zain Siddiqui',
    'license' : 'OPL-1',
    'sequence': 25,
    'depends' : ['sale_stock', 'sale'],
    'data' : [
        'security/ir.model.access.csv',
        'views/setu_abc_sales_analysis_report.xml',
        'views/res_company_views.xml',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
}
