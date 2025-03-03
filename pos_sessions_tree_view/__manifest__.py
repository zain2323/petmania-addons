{
    'name': 'POS Sessions Tree View',
    'version': '15.0.0.0.1',
    "category": 'Point of Sale',
    'summary': 'To Restrict POS features',
    'author': 'Zain Siddiqui',
    'company': 'Pynabyte Solutions',
    'maintainer': 'Pynabyte Solutions',
    'website': 'https://www.pynabyte.com/',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_session_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_sessions_tree_view/static/src/js/CashOpeningPopup.js',
            ],
        'web.assets_qweb': [
            'pos_sessions_tree_view/static/src/xml/Chrome.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
