# -*- coding: utf-8 -*-
{
    "name": "DXL Reordering Report",
    "version":"15.0.7",
    "category": "Sales",
    "depends": ['sale', 'stock', 'product_brand'],
    "data": [
        'security/ir.model.access.csv',
        'security/stock_security.xml',
        'views/reordering_report_view.xml',
        'views/product_category_view.xml',
        'wizard/reordering_report_wizard.xml',
    ],
    "installable": True,
    "application": True,
}
