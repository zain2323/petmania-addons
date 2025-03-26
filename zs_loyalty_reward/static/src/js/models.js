odoo.define('zs_pricelist_discount.models', function(require) {
 'use strict';

    var models = require('point_of_sale.models');
    models.load_fields('product.pricelist.item', 'extra_discount');
});
