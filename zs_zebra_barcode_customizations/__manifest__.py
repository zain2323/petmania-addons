{
    'name': 'Zebra Barcode Customizations',
    'version': '15.0.0.1',
    "category": 'Product',
    'author': 'Zain Siddiqui',
    'depends': ['base', 'td_zebra_barcode_labels', 'zs_inventory_planning_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/barcode_config_views.xml',
        'views/barcode_report.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
