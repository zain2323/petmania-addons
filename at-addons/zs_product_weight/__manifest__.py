{
    'name': 'Product Weight',
    'version': '15.0.3.0.0',
    'category': 'Sales',
    'website': 'https://www.pynabyte.com',
    'depends': ['sale_management', 'base', 'sale', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_report_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
