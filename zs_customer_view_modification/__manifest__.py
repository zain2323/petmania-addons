# -*- coding: utf-8 -*-
{
    'name': 'Customer View Modification',

    'summary': '',
    'author': "Zain Siddiqui",
    'license': "LGPL-3",
    'version': '15.0.0.1',

    'category': 'Base',
    'depends': ['base', 'sale', 'zs_product_company_type'],

    'data': [
        'data/assign_customer_categories.xml',
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/vet_pet_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
