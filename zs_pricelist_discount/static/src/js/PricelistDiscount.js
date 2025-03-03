odoo.define('custom_pos.PricelistDiscount', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const PricelistDiscount = ProductScreen => class extends ProductScreen {

        async _clickProduct(event) {
            await super._clickProduct(event);
            const product = event.detail;
            const order = this.env.pos.get_order();
            const pricelist = order ? order.pricelist : this.env.pos.default_pricelist;


            if (order && order.get_selected_orderline()) {
                order.get_selected_orderline().set_discount(0);
            }

            const discounted_products = pricelist.items.filter(item => item.product_tmpl_id[0] === product.product_tmpl_id);
            let extra_discount = 0;
            if (discounted_products.length > 0) {
                extra_discount = discounted_products[0].extra_discount;
            }
            if (extra_discount > 0) {
                discounted_products.forEach((discounted_product) => {
                    extra_discount = discounted_product.extra_discount;
                    if (extra_discount > 0 && (this.currentOrder.get_selected_orderline().get_quantity() === discounted_product.min_quantity || discounted_product.min_quantity === 0)) {
                        if (discounted_product.date_start && discounted_product.date_end) {
                            const currentDate = new Date().toISOString().split('T').join(' ').split('.')[0];
                            const dateStart = discounted_product.date_start
                            const dateEnd = discounted_product.date_end
                            console.log(currentDate)
                            console.log(dateEnd)
                            if (currentDate >= dateStart && currentDate <= dateEnd) {
                                this.currentOrder.get_selected_orderline().set_discount(extra_discount);
                            } else {
                                console.log("The current date is outside the range.");
                            }
                        } else {
                            this.currentOrder.get_selected_orderline().set_discount(extra_discount);
                        }
                    }

                })
            }
        }

        _setValue(val) {
            if (this.currentOrder.get_selected_orderline()) {
                if (this.state.numpadMode === 'quantity') {
                    const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                    if (!result) {
                        NumberBuffer.reset();
                        return;
                    }
                    if (this.currentOrder && this.currentOrder.get_selected_orderline()) {
                        this.currentOrder.get_selected_orderline().set_discount(0);
                    }
                    const pricelist = this.currentOrder ? this.currentOrder.pricelist : this.env.pos.default_pricelist;
                    const order = this.currentOrder;
                    const discounted_products = pricelist.items.filter(item => order.get_selected_orderline() && item.product_tmpl_id[0] === order.get_selected_orderline().get_product().product_tmpl_id);
                    console.log("products", discounted_products)
                    let extra_discount = 0;
                    if (discounted_products.length > 0) {
                        extra_discount = discounted_products[0].extra_discount;
                    }
                    if (extra_discount > 0) {
                        discounted_products.forEach((discounted_product) => {
                            extra_discount = discounted_product.extra_discount;
                            if (extra_discount > 0 && (this.currentOrder.get_selected_orderline().get_quantity() === discounted_product.min_quantity || discounted_product.min_quantity === 0)) {
                                if (discounted_product.date_start && discounted_product.date_end) {
                                    const currentDate = new Date().toISOString().split('T').join(' ').split('.')[0];
                                    const dateStart = discounted_product.date_start
                                    const dateEnd = discounted_product.date_end
                                    console.log(currentDate)
                                    console.log(dateEnd)
                                    if (currentDate >= dateStart && currentDate <= dateEnd) {
                                        this.currentOrder.get_selected_orderline().set_discount(extra_discount);
                                    } else {
                                        console.log("The current date is outside the range.");
                                    }
                                } else {
                                    this.currentOrder.get_selected_orderline().set_discount(extra_discount);
                                }
                            }

                        })
                    }

                } else {
                    super._setValue(val);
                }
            }
        }
    };

    // Register the custom component
    Registries.Component.extend(ProductScreen, PricelistDiscount);

    return PricelistDiscount;
});
