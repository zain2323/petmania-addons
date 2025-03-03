odoo.define('stock_no_negative.order_line', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var _t = core._t;

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity, keep_price) {
            var qty_available = this.pos.db.qty_by_product_id[this.product.id];
            if (Object.keys(this.order.screen_data).length > 0 && this.pos.config.restrict_out_of_stock && this.product.type == 'product' && this.product.categ.allow_negative_stock === false && this.product.allow_negative_stock === false && qty_available < quantity && this.quantity >= 0 && quantity) {
                Gui.showPopup('ErrorPopup',{
                    'title': _t("Insufficient Stock"),
                    'body':  _t("Product not available in stock."),
                });
                return false;
            } else {
                return _super_orderline.set_quantity.apply(this,arguments);
            }
        },
        check_reminder: async function () {
            var self = this;
            var qty_available = this.pos.db.qty_by_product_id[this.product.id];

            var all_product_line = this.order.orderlines.filter(function (orderline) {
                return self.product.id === orderline.product.id;
            });

            if (all_product_line.indexOf(self) === -1) {
                all_product_line.push(self);
            }

            var sum_qty = 0;
            all_product_line.forEach(function (line) {
                sum_qty += line.quantity;
            });

            if (qty_available < sum_qty) {
                await Gui.showPopup('ErrorPopup',{
                    'title': _t("Insufficient Stock"),
                    'body':  _t("Product not available in stock."),
                });
                return false;
            }
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        get_cart_qty: function (product) {
            var self = this;
            var all_product_line = this.orderlines.filter(function (orderline) {
                return product.id === orderline.product.id;
            });

            var sum_qty = 0;
            all_product_line.forEach(function (line) {
                sum_qty += line.quantity;
            });
            return sum_qty
        },
        add_product: async function(product, options){
            options = options || {};
            var is_refund = options.refunded_orderline_id;
            if (this.pos.config.restrict_out_of_stock && !is_refund) {
                var cart_qty = this.get_cart_qty(product);
                var qty_available = this.pos.db.qty_by_product_id[product.id] - cart_qty;
                if (cart_qty >= 0 && qty_available <= 0 && product.categ.allow_negative_stock === false && product.allow_negative_stock === false) {
                    await Gui.showPopup('ErrorPopup',{
                            'title': _t("Insufficient Stock"),
                            'body':  _t("Product not available in stock."),
                        });
                    return false;
                }
            }
            return _super_order.add_product.call(this, product, options);
        },
    });
});
