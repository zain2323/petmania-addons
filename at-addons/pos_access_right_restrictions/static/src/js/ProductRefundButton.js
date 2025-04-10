odoo.define('pos_access_right_restrictions.ProductRefundButtonExtension', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const RefundButton = require('point_of_sale.RefundButton');


    ProductScreen.addControlButton({
        component: RefundButton,
        condition: function () {
            return this.env.pos.user.show_product_refund_button != false;
        },
        position: ['replace', 'RefundButton'],
    });
});
