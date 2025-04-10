odoo.define('pos_access_right_restrictions.ProductInfoButtonExtension', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const ProductInfoButton = require('point_of_sale.ProductInfoButton');


    ProductScreen.addControlButton({
        component: ProductInfoButton,
        condition: function () {
            return this.env.pos.user.show_product_info_button != false;
        },
        position: ['replace', 'ProductInfoButton'],
    });
});
