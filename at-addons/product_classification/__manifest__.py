{
    'name': 'Product Classification',
    'version': '15.0.2.0.0',
    'category': 'Sales',
    'website': 'https://www.pynabyte.com',
    'depends': ['sale_management', 'base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_classification_views.xml',
        'views/sale_report_views.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
