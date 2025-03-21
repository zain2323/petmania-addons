# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vetinary Report',
    'version': '15.0.0.1',
    'author': 'Zain Siddiqui',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['stock', 'sale', 'zs_inventory_planning_report'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/groups.xml',
        # 'data/product_actions.xml',
        # 'data/optimize_quantities.xml',
        # 'data/audit_sequence.xml',
        # 'data/adjust_inventory.xml',
        'views/vetinary_config_view.xml',
        'views/vet_machine_report_view.xml',
        'views/vet_machine_report_wizard_view.xml',
        'views/vet_machine_consolidated_report_view.xml',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
}
