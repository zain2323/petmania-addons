odoo.define('pos_lock_mode.lock_mode', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');

    const ExtendedNumpadWidget = NumpadWidget => class extends NumpadWidget {

        async getPassword() {
            const userResponse = await Gui.showPopup(
              'PasswordInputPopup',
              { 
                title: 'Enter Password',
                body: 'Please enter the password to continue.'
              }
            );
            return userResponse
          }

        async changeMode(mode) {
            if (!this.hasPriceControlRights && mode === 'price') {
                return;
            }
            if (!this.hasManualDiscount && mode === 'discount') {
                return;
            }

            if (this.env.pos.config.lock_discount == true && mode === 'discount') {
                const userResponse = await this.getPassword()
                if (userResponse.payload !== this.env.pos.config.discount_password) {
                    await Gui.showPopup('ErrorPopup', {
                        'title': _t('Error'),
                        'body': _t('Incorrect password. Please try again'),
                    });
                    return
                }
            }
            this.trigger('set-numpad-mode', { mode });
        }
    }

    ExtendedNumpadWidget.template = 'NumpadWidget';
    Registries.Component.extend(NumpadWidget, ExtendedNumpadWidget);

    return ExtendedNumpadWidget;
});