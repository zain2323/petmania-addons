# -*- coding: utf-8 -*-
{
    "name": "DXL Price Control EXT",
    "version": "15.0.1",
    "license": 'OPL-1',
    "summary": """
        Price Control EXT
    """,
    'category': 'Sales',
    'depends': [
        'sale_management',
        'account'
    ],
    'data': [
        'security/price_security.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
