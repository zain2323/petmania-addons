{
    'name': 'Product Company Type',
    'version': '15.0.4.0.0',
    'category': 'Sales',
    'website': 'https://www.pynabyte.com',
    'depends': ['sale_management', 'base', 'sale', 'account', 'stock', 'product_brand'],
    'data': [
        'security/ir.model.access.csv',
        'views/company_type_views.xml',
        'views/sale_report_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
