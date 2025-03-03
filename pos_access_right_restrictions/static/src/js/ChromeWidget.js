odoo.define('pos_access_right_restrictions.CustomChrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const ChromeWidgetAccessRight = Chrome => class extends Chrome {
        /**
        * Hide Orders button on the POS
        */
        get showTicketButton() {
            let condition;
            try {
                condition = this.env && this.env.pos && this.env.pos.user && this.env.pos.user.show_orders_menu_button === false;
            }
            catch {
                condition = undefined;
            }
            if (condition == false || condition == null || condition == undefined) {
                return true
            }
            return false
        }

    };
    Registries.Component.extend(Chrome, ChromeWidgetAccessRight);
    return Chrome;
});
