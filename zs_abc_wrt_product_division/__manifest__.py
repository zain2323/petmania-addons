# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sales Contribution Classification',
    'version' : '15.0.0.0.8',
    'license' : 'OPL-1',
    'sequence': 25,
    'depends' : ['sale_stock', 'sale', 'zs_scm_grading', 'zs_product_company_type', 'product_brand', 'zs_inventory_planning_report'],
    'data' : [
        'security/ir.model.access.csv',
        'data/cron_job.xml',
        'views/product_template_views.xml',
        'views/min_max_config_views.xml',
        'views/min_max_config_storage_views.xml',
        'views/purchase_views.xml',
        # 'views/setu_abc_xyz_analysis_report.xml',
        # 'views/setu_abc_sales_frequency_analysis_report.xml',
    ],
    'application': True,
    'pre_init_hook': 'pre_init',
}
