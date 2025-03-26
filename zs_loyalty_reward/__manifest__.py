# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Loyalty Reward',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        "views/loyalty_reward_config_views.xml",
    ],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'zs_pricelist_discount/static/src/js/models.js',
    #         'zs_pricelist_discount/static/src/js/PricelistDiscount.js',
    #
    #     ],
    #     # 'web.assets_qweb': [
        #     'pos_access_right_restrictions/static/src/xml/TicketButton.xml',
        # ],
    # },
    'installable': True,
    'application': True,
    'auto_install': False,
}
