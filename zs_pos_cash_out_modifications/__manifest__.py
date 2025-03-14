{
    'name': 'Pos Cash Out Modifications',
    'version': '15.0.0.0.1',
    "category": 'Point of Sale',
    'author': 'Zain Siddiqui',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_employee_secret_key.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_pos_cash_out_modifications/static/src/js/cashMoveButton.js',
            'zs_pos_cash_out_modifications/static/src/js/headerButton.js',

        ],
        'web.assets_qweb': [
            'zs_pos_cash_out_modifications/static/src/xml/CashMoveButton.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
