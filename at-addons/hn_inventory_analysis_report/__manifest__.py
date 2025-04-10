{
    'name': "Inventory Analysis Report",
    'description': "",
    'category': 'customization',
    'sequence': 10,
    'version': '15.0.1.0',
    'depends': [ 'stock','product','product_brand','purchase_stage' ], 
    'data': [
        'views/stock_warehouse.xml',
        'views/stock_location.xml',
        'wizard/inventory_analysis_report.xml',
        'wizard/inventory_analysis_data_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo' : [] ,
    'qweb' : [],
    'installable' : True, 
    'application' : False,
    'auto_install' : False,
    'license': 'LGPL-3',
    'pre_init_hook' : 'pre_init_hook'
}
