# -*- coding: utf-8 -*-
{
    'name': 'Customer Attributes',

    'summary': '',
    'author': "Zain Siddiqui",
    'license': "LGPL-3",
    'version': '15.0.0.2',

    'category': 'Sales',
    'depends': ['base', 'sale', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/customer_attributes.xml',
        'views/partner_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
