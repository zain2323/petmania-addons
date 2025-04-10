# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Price Lists Discount',
    'version' : '15.0.0.0',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale'],
    'data': [
        "views/price_list_view.xml",
        "views/product_pricelist_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_pricelist_discount/static/src/js/models.js',
            'zs_pricelist_discount/static/src/js/PricelistDiscount.js',

        ],
        # 'web.assets_qweb': [
        #     'pos_access_right_restrictions/static/src/xml/TicketButton.xml',
        # ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
