odoo.define('stock_no_negative.DB', function (require) {
"use strict";
    var PosDB = require('point_of_sale.DB');

    PosDB.include({
        init: function(options){
            this._super(options);
            this.qty_by_product_id = {};
        },
    });
});