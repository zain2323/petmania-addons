{
    'name': 'POS Restrictions',
    'version': '15.0.0.0.1',
    "category": 'Point of Sale',
    'summary': 'To Restrict POS features',
    'description': 'This app allows you to enable or disable POS features '
                   'based on the access rights granted to the user',
    'author': 'Zain Siddiqui',
    'company': 'Pynabyte Solutions',
    'maintainer': 'Pynabyte Solutions',
    'website': 'https://www.pynabyte.com/',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/res_users_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_access_right_restrictions/static/src/js/models.js',
            'pos_access_right_restrictions/static/src/js/ProductInfoButton.js',
            'pos_access_right_restrictions/static/src/js/ProductRefundButton.js',
            'pos_access_right_restrictions/static/src/js/ChromeWidget.js',

        ],
        'web.assets_qweb': [
            'pos_access_right_restrictions/static/src/xml/TicketButton.xml',
            'pos_access_right_restrictions/static/src/xml/Chrome.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
