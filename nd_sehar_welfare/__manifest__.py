# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sehar Welfare',
    'version' : '15.0.0.1',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        "views/pos_config_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'nd_sehar_welfare/static/src/js/PasswordInputPopup.js',
            'nd_sehar_welfare/static/src/js/ProductScreen.js',

        ],
        'web.assets_qweb': [
            'nd_sehar_welfare/static/src/xml/PasswordInputPopupSeharWelfare.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
