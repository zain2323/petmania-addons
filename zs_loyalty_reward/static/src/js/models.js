odoo.define('zs_loyalty_reward.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var _super_pos_model = models.PosModel.prototype;

    models.load_fields('product.product', ['purchase_count']);
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            _super_pos_model.initialize.apply(this, arguments);
            this.reward_configs = [];
            // Load reward configurations from the server
            this.load_reward_configs();
        },

        // Load reward configurations from the backend
        load_reward_configs: function () {
            var self = this;
            rpc.query({
                model: 'loyalty.reward.config',
                method: 'search_read',
                args: [[], ['product_id', 'purchase_count']],
            }).then(function (result) {
                self.reward_configs = result;
            });
        },

        // Get the purchase count for a product (if it has a reward config)
        get_purchase_count_for_product: function (product) {
            var reward_config = this.reward_configs.find(function (config) {
                return config.product_id[0] === product.id;
            });
            return reward_config ? reward_config.purchase_count : null;
        },
    });

    // Extend the Orderline model to include the purchase count
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attributes, options) {
            _super_orderline.initialize.apply(this, arguments);
            this.purchase_count = this.get_purchase_count();
        },

        export_for_printing: function () {
            const result = _super_orderline.export_for_printing.apply(this, arguments);
            const product = this.get_product();
            const order = this.order;
            const client = order.get_client();
            const tracking = client?.reward_tracking_data?.[product.id];
            console.log("client", client)
            console.log("tracking", tracking)
            if (tracking) {
                const remaining = tracking.required - tracking.filled;
                console.log("remaining", remaining)

                result.filled_stars = Array.from({length: tracking.filled}, (_, i) => i);
                result.empty_stars = Array.from({length: remaining}, (_, i) => i);
            } else {
                result.filled_stars = [];
                result.empty_stars = [];
            }

            return result;
        },

        // Get the purchase count for this orderline's product
        get_purchase_count: function () {
            var purchase_count = null;
            if (this.product) {
                purchase_count = this.pos.get_purchase_count_for_product(this.product);
            }
            return purchase_count;
        },
    });
});
