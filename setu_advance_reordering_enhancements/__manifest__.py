# -*- coding: utf-8 -*-
{
    # Module Info
    'name': "Advance Reordering Enhancements",
    'version': '1.6',
    'category': 'stock',
    'summary': """This module is for the enhancements of Advance Reordering module.
               1. Functionality to stock reordering by SCM Grading Category.""",
    'description': "This module is for the enhancements of Advance Reordering module.",

    # Author
    'author': "Ahmer Shahid <ahmershahid666@gmail.com>",
    'website': "+923209444456",

    # Dependencies
    'depends': ['setu_advance_reordering', 'zs_scm_grading'],

    # Data
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/stock_warehouse_orderpoint.xml',
        'views/stock_warehouse_orderpoint_category.xml',
        'views/purchase_views.xml',
    ],

    # Technical Specif.
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
