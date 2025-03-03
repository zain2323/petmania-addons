{
    'name': 'Company Stages',
    'version': '15.0.0.1',
    'category': 'Base',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'data/update_stages.xml',
        'views/res_company_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zs_company_stages/static/src/js/systray.js',
        ],
        'web.assets_qweb': [
            'zs_company_stages/static/src/xml/CompanyStageSystray.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
