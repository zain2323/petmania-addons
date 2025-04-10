{
    'name' : 'Sales Order Warehouse On Hand QTY',
    'version' : '15.0.0.0',
    'author':'Zain Siddiqui',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends' : ['sale_management','stock'],
    'data': [
        'views/sale_line_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,

}
