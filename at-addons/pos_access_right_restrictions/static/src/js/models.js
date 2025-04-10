odoo.define('pos_access_right_hr.models', function(require) {
 'use strict';

    var models = require('point_of_sale.models');
    models.load_fields('res.users', 'show_product_info_button');
    models.load_fields('res.users', 'show_product_refund_button');
    models.load_fields('res.users', 'show_orders_menu_button');
    models.load_fields('res.users', 'show_edit_onhand_qty');
  
});
