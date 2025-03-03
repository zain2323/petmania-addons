odoo.define('stock_no_negative.models', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var PosModel = models.PosModel;

    models.PosModel = PosModel.extend({
        on_stock_notification: function (stock_quant) {
            var self = this;
            var product_ids = stock_quant.map(function (item) {
                return item.product_id[0];
            });

            if (this.config && this.config.restrict_out_of_stock && product_ids.length > 0) {
                $.when(self.qty_sync(product_ids)).done(function () {
                    self.refresh_qty();
                });
            }
        },
        qty_sync: function (product_ids) {
            var self = this;
            var done = new $.Deferred();
            if (this.config && this.config.restrict_out_of_stock) {
                rpc.query({
                    model: 'stock.quant',
                    method: 'get_qty_available',
                    args: [this.config.picking_type_id[0], product_ids]
                }).then(function (res) {
                    self.recompute_qty_in_pos_location(product_ids, res);
                    done.resolve();
                });

            } else {
                done.resolve();
            }
            return done.promise();
        },
        compute_qty_in_pos_location: function (res) {
            var self = this;
            // self.db.qty_by_product_id = {};
            res.forEach(function (item) {
                var product_id = item.product_id[0];
                if (!self.db.qty_by_product_id[product_id]) {
                    self.db.qty_by_product_id[product_id] = item.available_quantity;
                } else {
                    self.db.qty_by_product_id[product_id] += item.available_quantity;
                }
            })
        },
        recompute_qty_in_pos_location: function (product_ids, res) {
            var self = this;
            var res_product_ids = res.map(function (item) {
                return item.product_id[0];
            });

            var out_of_stock_ids = product_ids.filter(function (id) {
                return res_product_ids.indexOf(id) === -1;
            });

            out_of_stock_ids.forEach(function (id) {
                self.db.qty_by_product_id[id] = 0;
            });

            res_product_ids.forEach(function (product_id) {
                self.db.qty_by_product_id[product_id] = false;
            });

            res.forEach(function (item) {
                var product_id = item.product_id[0];

                if (!self.db.qty_by_product_id[product_id]) {
                    self.db.qty_by_product_id[product_id] = item.available_quantity;
                } else {
                    self.db.qty_by_product_id[product_id] += item.available_quantity;
                }
            });
        },
        refresh_qty: function () {
            var self = this;
            $('.product-list').find('.qty-tag').each(function () {
                var $product = $(this).parents('.product');
                var id = parseInt($product.attr('data-product-id'));
                var prd = self.db.get_product_by_id(id);
                var qty = self.db.qty_by_product_id[id];

                if (qty === false) {
                    return;
                }

                if (qty === undefined || qty <= 0) {
                    qty = qty || 0;
                }

                $(this).text(qty).show('fast');
            });
        },
        get_product_image_url: function (product) {
            return window.location.origin + '/web/image?model=product.product&field=image_medium&id=' + product.id;
        }
    });
});
