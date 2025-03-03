{
    'name': 'POS Sessions Payment',
    'version': '15.0.0.0.1',
    "category": 'Point of Sale',
    'author': 'Zain Siddiqui',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/update_session_payments.xml',
        'views/pos_session_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
