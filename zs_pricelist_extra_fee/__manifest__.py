# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Price Lists Extra Fee',
    'version' : '15.0.0.0',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product'],
    'data': [
        "views/price_list_view.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
