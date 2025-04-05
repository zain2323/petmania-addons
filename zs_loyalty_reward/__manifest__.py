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
        "views/customer_purchase_tracking_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_loyalty_reward/static/src/js/models.js',
            'zs_loyalty_reward/static/src/js/RewardStreak.js',

        ],
        'web.assets_qweb': [
            'zs_loyalty_reward/static/src/xml/reward_streak.xml',
            'zs_loyalty_reward/static/src/xml/custom_pos_reciept.xml'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
