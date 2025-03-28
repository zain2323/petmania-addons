odoo.define('zs_customer_view_modification.GiftCardPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');


    class GiftCardPopupCode extends AbstractAwaitablePopup {
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
        copyToClipboard() {
            const codeElement = document.querySelector('.gift-card-code');
            if (codeElement) {
                const range = document.createRange();
                range.selectNode(codeElement);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                document.execCommand('copy');
                selection.removeAllRanges();

                // Show a temporary message
                const notification = document.createElement('div');
                notification.className = 'notification';
                notification.textContent = this.env._t('Code copied to clipboard');
                notification.style.position = 'fixed';
                notification.style.bottom = '20px';
                notification.style.right = '20px';
                notification.style.backgroundColor = '#4CAF50';
                notification.style.color = 'white';
                notification.style.padding = '10px 20px';
                notification.style.borderRadius = '4px';
                notification.style.zIndex = '10000';
                document.body.appendChild(notification);

                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
        }
    }
    GiftCardPopupCode.template = 'GiftCardPopup';
    GiftCardPopupCode.defaultProps = {
        confirmText: _lt('Ok'),
        title: _lt('Gift Card Found'),
        body: '',
        code: '',
        balance: '',
        expiration: '',
        customerName: ''
    };

    Registries.Component.add(GiftCardPopupCode);

    return GiftCardPopupCode;
});