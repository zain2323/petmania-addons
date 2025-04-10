odoo.define('custom_pos.PricelistDiscount', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PricelistDiscount = ProductScreen => class extends ProductScreen {

        async _clickProduct(event) {
            await super._clickProduct(event);
            const product = event.detail;
            const order = this.env.pos.get_order();
            const pricelist = order ? order.pricelist : this.env.pos.default_pricelist;
            const discounted_product = pricelist.items.filter(item => item.product_tmpl_id[[0]] === product.product_tmpl_id);
            let extra_discount = 0;
            if (discounted_product.length > 0){
                extra_discount = discounted_product[0].extra_discount;
            }
            if (extra_discount > 0){
                order.get_selected_orderline().set_discount(extra_discount)
            }

        }
    };

    // Register the custom component
    Registries.Component.extend(ProductScreen, PricelistDiscount);

    return PricelistDiscount;
});
