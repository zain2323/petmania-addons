# -*- coding: utf-8 -*-

{
    'name': "POS LOCK DISCOUNT",
    'author': "Zain Siddiqui",
    'category': 'Point Of Sale',
    'license': "LGPL-3",
    'version': '15.0.0.0',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'pos_lock_price_discount/static/src/xml/PasswordInputPopup.xml',
        ],
        'point_of_sale.assets': [
            'pos_lock_price_discount/static/src/js/PasswordInputPopup.js',
            'pos_lock_price_discount/static/src/js/lock_price_discount.js',
        ],
    },
}
