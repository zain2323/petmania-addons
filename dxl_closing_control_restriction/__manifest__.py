{
    "name": "DXL Clogin Control Restriction",
    "version": "15.0.2",
    "author": "Dymaxel Systems",
    "license": 'OPL-1',
    "summary": """DXL Clogin Control Restriction""",
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale', 'dxl_closing_control_restriction_group',
    ],
    'data': [
        'security/menu_security.xml',
        'views/pos_config_view.xml',
        'views/pos_session_view.xml',
    ],
    'assets': {
         'point_of_sale.assets': [
            'dxl_closing_control_restriction/static/src/js/pos.js',
        ],
        'web.assets_qweb': [
            'dxl_closing_control_restriction/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
