{
    'name': 'Brand Recievables',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'website': 'https://www.pynabyte.com',
    'depends': ['sale_management', 'base', 'sale', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
