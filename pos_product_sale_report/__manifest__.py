# -*- coding: utf-8 -*-
{
    'name': 'POS Sales Report',

    'description': """
        POS Sales Reports
    """,

    'summary': '',

    'category': "POS",
    'version': '15.0.2',
    'author': "Numla Ltd.",
    'website': "https://www.numla.com/",
    'license': "Other proprietary",

    'depends': ['base', 'point_of_sale', 'stock', 'product_brand'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/branding_filters_view.xml',
        'views/menu.xml',

        'report/pos_sale_report_template.xml',
        'report/pos_sale_report_action.xml',
    ],

    'external_dependencies': {
        'python': ['pandas'],
    },

    'installable': True,
    'auto_install': False,
    'application': False,

}
