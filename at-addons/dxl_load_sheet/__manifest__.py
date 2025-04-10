# -*- coding: utf-8 -*-
{
    'name': 'Dxl Load Sheet Report',
    'version': '15.0.5',
    'author': 'Dymaxel System',
    'category': 'Sales',
    'description': """Load Sheet Report""",
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'data/ir_sequence_data.xml',
        'views/load_sheet_view.xml',
        'wizard/load_sheet_wizard.xml',
    ],
    "license": 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
