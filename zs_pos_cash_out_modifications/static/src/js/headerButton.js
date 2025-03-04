odoo.define('zs_pos_cash_out_modifications.pos_header_button', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');
    const core = require('web.core');
    const _t = core._t;
    const {Gui} = require('point_of_sale.Gui');


    const CustomHeaderButton = (HeaderButton) => class extends HeaderButton {
        async onClick() {
            console.log(this.env);
            console.log(this.env.pos);
            console.log(this.env.pos.cashed_out);

            // Check if cashier has cashed out
            if (!this.env.pos.cashed_out) {
                await Gui.showPopup('ErrorPopup', {
                    'title': _t('Error'),
                    'body': _t('Please cash out first before closing the session'),
                });
                return;
            }

            // Continue with the default close session process
            await super.onClick();
        }
    };

    Registries.Component.extend(HeaderButton, CustomHeaderButton);

    return CustomHeaderButton;
});
