odoo.define('zs_pos_cash_out_modifications.pos_header_button', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');
    const core = require('web.core');
    const _t = core._t;
    const {Gui} = require('point_of_sale.Gui');


    const CustomHeaderButton = (HeaderButton) => class extends HeaderButton {
        async onClick() {

            // Check if cashier has cashed out
            if (!this.env.pos.pos_session.is_cashed_out || !this.env.pos.pos_session.is_cashed_out_last) {
                await Gui.showPopup('ErrorPopup', {
                    'title': _t('Error'),
                    'body': _t('Please cash out first before closing the session'),
                });
                return;
            }

            // Continue with the default close session process
            const info = await this.env.pos.getClosePosInfo();
            console.log(info)
            info.state.acceptClosing = true;
            this.showPopup('ClosePosPopup', { info: info });
            // await super.onClick();
        }
    };

    Registries.Component.extend(HeaderButton, CustomHeaderButton);

    return CustomHeaderButton;
});
