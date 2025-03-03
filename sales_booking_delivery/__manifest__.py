# -*- coding: utf-8 -*-
{
    "name" : "Sale Booking Delivery",
    "version" : "15.0.0",
    "category" : "Sales",
    "depends" : [
        'bi_pos_multi_shop',
        'sale_stock',
        'sale_management',
        'sale_advance_payment',
    ],
    "data": [
    	'security/order_security.xml',
        'security/ir.model.access.csv',
        'wizard/deliver_rider_wizard.xml',
        'views/res_config_settings.xml',
    	'views/sale_view.xml',
        'views/shop_view.xml',
    	],
    "application": True,
    "installable": True,
}