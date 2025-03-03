# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'POS Alternate Product name',
    'version' : '15.0.0.0',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale'],
    'data': [
        "views/product_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_alternate_product_name/static/src/js/models.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
