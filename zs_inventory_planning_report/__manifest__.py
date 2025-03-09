# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inventory Planning Report',
    'version': '15.0.0.5',
    'author': 'Zain Siddiqui',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['stock', 'sale', 'zs_product_company_type', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/groups.xml',
        'data/product_actions.xml',
        'data/optimize_quantities.xml',
        'data/audit_sequence.xml',
        'data/adjust_inventory.xml',
        'views/inventory_audit_report_view.xml',
        'views/inventory_planning_report_view.xml',
        'views/inventory_planning_view.xml',
        'views/purchase_views.xml',
        'views/inventory_optimisation_report_view.xml',
        'views/out_of_stock_report_view.xml',
        'views/branch_storage_configuration_report_view.xml',
        'views/branch_value_configuration_report_view.xml',
        'views/product_account_report_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'zs_inventory_planning_report/static/src/js/models.js',
        ],
    },
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
}
