# -*- coding: utf-8 -*-
{
    'name': 'Products',

    'summary': '',
    'author': "Sajjad Hussain",
    'website': "https://www.linkedin.com/in/sajjad-hussain-278692219/",
    'license': "LGPL-3",
    'version': '15.0.8',

    'category': 'Stock',
    'depends': ['base', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_bypass_company_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
