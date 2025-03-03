# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'POS  Bank Charges',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale'],
    'data': [
        "views/pos_config_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_pos_bank_charges/static/src/js/models.js',

        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
