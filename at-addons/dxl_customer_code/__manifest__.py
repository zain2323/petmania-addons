# -*- coding: utf-8 -*-
{
    'name': 'Dxl Customer Code',
    'version': '15.0.2',
    'author': 'Dymaxel System',
    'category': 'Sales',
    'description': """Customer Code""",
    'depends': ['contacts', 'sale', 'stock', 'account', 'dxl_print_ntn_strn_v15'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_code_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice.xml',
        'views/stock_picking.xml',
        'report/account_invoice_report.xml',
    ],
    "license": 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
