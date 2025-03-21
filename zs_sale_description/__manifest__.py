# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Subscription Customization',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'sale_subscription', 'sale'],
    'data': [
        "views/sale_subscription_view.xml",
        "views/account_move_view.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
