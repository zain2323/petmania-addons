# -*- coding: utf-8 -*-
{
    'name': 'Customer View Modification',

    'summary': '',
    'author': "Zain Siddiqui",
    'license': "LGPL-3",
    'version': '15.0.0.1',

    'category': 'Base',
    'depends': ['base', 'sale', 'contacts', 'point_of_sale'],

    'data': [
        'data/assign_customer_categories.xml',
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/vet_pet_view.xml',
        'views/customer_category_config_views.xml',
        'views/customer_tag_views.xml',
        'views/gift_card_config_views.xml',
        'views/gift_card_history_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'zs_customer_view_modification/src/static/js/GiftCardPopup.js',
            'zs_customer_view_modification/static/src/js/clientScreen.js',
            'zs_customer_view_modification/static/src/js/ClientLine.js',
        ],
        'web.assets_qweb': [
            'zs_customer_view_modification/static/xml/ClientLine.xml',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,

}
