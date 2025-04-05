# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Product Suspension',
    'version' : '15.0.0.1',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['base', 'product', 'product_brand', 'zs_product_modifications', 'zs_abc_wrt_product_division'],
    'data': [
        'security/ir.model.access.csv',
        'data/suspension_actions.xml',
        'data/suspend_products_cron.xml',
        'views/product_suspension_views.xml',
        'views/product_brand_views.xml',
        'views/product_vendor_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
