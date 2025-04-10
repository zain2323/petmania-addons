odoo.define('zs_inventory_planning_report.AuditReportCustomizations', function (require) {
    "use strict";

    const models = require('point_of_sale.models');
    const core = require('web.core');
    const _t = core._t;
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');

    models.load_fields('product.product', 'available_in_pos_company');
    models.load_fields('product.template', 'available_in_pos_company');
    console.log("hello")

    const AvailableInPos = ProductScreen => class extends ProductScreen {

        async _clickProduct(event) {
            const order = this.env.pos.get_order();
            await super._clickProduct(event);
            console.log(order.get_selected_orderline())
            const selected_product = order.get_selected_orderline().product
            if (!selected_product.available_in_pos_company) {
                await Gui.showPopup('ErrorPopup', {
                    'title': _t('Error'),
                    'body': _t('Audit is in progress. Please try again later'),
                });
                order.remove_orderline(order.get_selected_orderline())
            }
        }
    };

    // Register the custom component
    Registries.Component.extend(ProductScreen, AvailableInPos);

    return AvailableInPos;
});
