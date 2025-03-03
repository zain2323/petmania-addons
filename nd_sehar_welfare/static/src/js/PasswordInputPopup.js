odoo.define('nd_sehar_welfare.PasswordInputPopupSeharWelfare', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class PasswordInputPopupSeharWelfare extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }
    }
    PasswordInputPopupSeharWelfare.template = 'PasswordInputPopupSeharWelfare';
    PasswordInputPopupSeharWelfare.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
        startingValue: '',
    };

    Registries.Component.add(PasswordInputPopupSeharWelfare);

    return PasswordInputPopupSeharWelfare;
});
