# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Product Notifier',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/product_notifier_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
