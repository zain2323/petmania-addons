# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    'name': 'Odoo Power BI Connector',
    'version': '3.2.0',
    'category': 'Generic Modules',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'https://store.webkul.com/odoo-powerbi-connector.html',
    'live_test_url': 'https://odoodemo.webkul.com/?module=odoo_powerbi_connect',
    'sequence': 1,
    'license': "Other proprietary",
    'summary': 'Powerbi Connector',
    'description': """

Odoo Powerbi Connector
=======================

This Brilliant Module will Connect Odoo with Powerbi and synchronise Data.
--------------------------------------------------------------------------


Some of the brilliant feature of the module:
--------------------------------------------

    1. Import/Export Workspaces

    2. Export newly created datasets.

    3. Export/Update/Delete any model's data in tables.

    4. Import powerbi reports and view on odoo.

    5. Import powerbi dashboards and view on odoo.

    6. Create dynamic server actions for any model.

    7. Configure cron to auto sync data for any model.

This module works very well with latest version of Odoo 15.0
------------------------------------------------------------------------------
    """,
    'depends': [
        'base'
    ],
    'data': [
        'security/powerbi_connector_security.xml',
        'security/ir.model.access.csv',

        'data/powerbi_sequence.xml',
        'data/powerbi_server_actions.xml',
	    'data/powerbi_cron.xml',

        'wizard/powerbi_message_wizard_view.xml',
        'wizard/table_column_wizard_view.xml',
        'wizard/powerbi_wizard_view.xml',
        'wizard/powerbi_report_wizard_view.xml',
        'wizard/powerbi_dashboard_wizard_view.xml',
        'wizard/powerbi_credentials_wizard_view.xml',

        'views/powerbi_connection_view.xml',
        'views/powerbi_dataset_view.xml',
        'views/powerbi_table_view.xml',
        'views/powerbi_workspace_view.xml',
        'views/powerbi_dashboards_view.xml',
        'views/powerbi_reports_view.xml',
        'views/sync_history_view.xml',
        'views/powerbi_menus.xml',

        'data/demo/powerbi_demo_data.xml',
    ],

    'assets': {
        'web.assets_backend': [
            '/odoo_powerbi_connect/static/src/js/powerbi.js',
            'https://cdnjs.cloudflare.com/ajax/libs/powerbi-client/2.18.2/powerbi.min.js'
        ]
    },

    'external_dependencies': {'python' : ['msal']},
    'images': ['static/description/banner.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'price': 299,
    'currency': 'USD',
    'pre_init_hook': 'pre_init_check',
}
