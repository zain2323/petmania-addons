odoo.define('zs_alternate_product_name.AlternateProductName', function (require) {
    "use strict";

    const models = require('point_of_sale.models');
    const core = require('web.core');
    const _t = core._t;

    models.load_fields('product.product', 'use_secondary_name');
    models.load_fields('product.product', 'secondary_name');

    models.load_fields('product.template', 'use_secondary_name');
    models.load_fields('product.template', 'secondary_name');

    const OrderlineSuper = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            const result = OrderlineSuper.export_for_printing.apply(this, arguments);
            if (this.get_product().use_secondary_name) {
                result.product_name_wrapped = [this.get_product().secondary_name]
            }
            return result;
        },
    });
});
