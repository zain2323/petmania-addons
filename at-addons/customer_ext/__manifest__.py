# -*- coding: utf-8 -*-
{
    'name': 'Customer Ext',

    'summary': '',
    'author': "Sajjad Hussain",
    'website': "https://www.linkedin.com/in/sajjad-hussain-278692219/",
    'license': "LGPL-3",
    'version': '15.0.7',

    'category': 'Sales',
    'depends': ['base', 'sale', 'account', 'base_address_city', 'base_address_extended'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'views/customer_order_booker.xml',
        'views/customer_type.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/sale_report.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
