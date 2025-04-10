# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Customer Code',
    'version' : '15.0.0.0',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['sale_management','stock'],
    'data': [
        "views/res_partner_view.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
