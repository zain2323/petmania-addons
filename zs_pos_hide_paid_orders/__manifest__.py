# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Pos hide paid orders',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale', 'point_of_sale'],
    'data': [

    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_pos_hide_paid_orders/static/src/js/TicketScreen.js',
        ],
        'web.assets_qweb': [
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
