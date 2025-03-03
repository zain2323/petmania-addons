odoo.define('stock_no_negative.init', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');

    models.load_fields('product.category', 'allow_negative_stock');
    models.load_fields('product.product', ['type', 'allow_negative_stock']);

    models.load_models([{
        loaded: function (self) {
        this.stock_location_ids = [];

        var done = new $.Deferred();

        if (!self.config.restrict_out_of_stock) {
            return done.resolve();
        }
        if (self.config.restrict_out_of_stock) {
            rpc.query({
                model: 'stock.quant',
                method: 'get_qty_available',
                args: [self.config.picking_type_id[0]]
            }).then(function (res) {
                self.stock_location_ids = _.uniq(res.map(function (item) {
                    return item.location_id[0];
                }));
                self.compute_qty_in_pos_location(res);
                done.resolve();
            });
        }
        return done;
        }
    }],
    {
    after: 'account.journal' // nearly at the end of steps, after stock,location and product step
    });
});