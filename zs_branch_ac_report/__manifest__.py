# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'AC Machine Report',
    'version': '15.0.0.1',
    'author': 'Zain Siddiqui',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['stock', 'sale', 'zs_inventory_planning_report'],
    'data': [
        'security/ir.model.access.csv',
        'data/generate_ac_report.xml',
        'views/ac_config_view.xml',
        'views/ac_machine_report_view.xml',
        'views/ac_machine_report_wizard_view.xml',
        'views/ac_machine_consolidated_report_view.xml',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'application': True,
}
