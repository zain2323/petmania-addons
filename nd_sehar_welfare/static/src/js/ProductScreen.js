odoo.define('nd_sehar_welfare.ProductScreen', function (require) {
    "use strict";

    const models = require('point_of_sale.models');
    const core = require('web.core');
    const _t = core._t;
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');

    const SeharWelfare = ProductScreen => class extends ProductScreen {

        async getPassword() {
            return await Gui.showPopup('PasswordInputPopupSeharWelfare', {
                title: 'Enter Password',
                body: 'Please enter the password to continue with this product.',
                startingValue: ''
            })
        }

        async _clickProduct(event) {
            const order = this.env.pos.get_order();
            await super._clickProduct(event);

            const sehar_welfare_product_ids = this.env.pos.config.sehar_welfare_product_lines
            const passwords = [this.env.pos.config.sehar_welfare_password_1, this.env.pos.config.sehar_welfare_password_2]

            const sehar_welfare_products = []
            const lines = await this.env.pos.rpc({
                model: 'sehar.welfare.product.line', method: 'read', args: [sehar_welfare_product_ids, ['product_id']],
            });

            lines.forEach(line => {
                const productId = line.product_id[0];
                sehar_welfare_products.push(productId);
            });

            const selected_product = order.get_selected_orderline().product.id
            if (sehar_welfare_products.includes(selected_product)) {
                const userResponse = await this.getPassword()
                if (!passwords.includes(userResponse.payload)) {
                    await Gui.showPopup('ErrorPopup', {
                        'title': _t('Error'), 'body': _t('Incorrect password. Please try again'),
                    });
                    order.remove_orderline(order.get_selected_orderline())
                    return
                }
            }
        }
    };

    // Register the custom component
    Registries.Component.extend(ProductScreen, SeharWelfare);

    return SeharWelfare;
});
