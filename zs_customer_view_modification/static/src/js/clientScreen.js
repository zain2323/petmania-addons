odoo.define('zs_customer_view_modification.ClientListScreen', function (require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const models = require('point_of_sale.models');

    // Extend the ClientListScreen class
    const PosClientListScreenInherit = ClientListScreen => class extends ClientListScreen {
        // Override the confirm method instead of clickClient
        async confirm() {
            // If there's a selected client, check for gift cards
            if (this.state.selectedClient) {
                try {
                    // Get gift cards for the selected customer via RPC
                    const giftCards = await this.rpc({
                        model: 'gift.card',
                        method: 'search_read',
                        args: [
                            [['partner_id', '=', this.state.selectedClient.id], ['state', '=', 'valid']],
                            ['code', 'balance', 'expired_date'] // Adjust fields as needed
                        ],
                        kwargs: {
                            limit: 1,
                        },
                    });

                    // If gift cards exist, show popup with gift card details
                    if (giftCards && giftCards.length > 0) {
                        const giftCard = giftCards[0];
                        // await this.showPopup('GiftCardPopupCode', {
                        //     title: this.env._t('Gift Card Found'),
                        //     code: giftCard.code,
                        //     balance: this.env.pos.format_currency(giftCard.balance),
                        //     expiration: giftCard.expiration_date || '',
                        //     customerName: this.state.selectedClient.name
                        // });
                        await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Gift Card Found'),
                            body: this.env._t(`Customer ${this.state.selectedClient.name} has a gift card with code: ${giftCard.code}
                                            Balance: ${this.env.pos.format_currency(giftCard.balance)}
                                            Expiration: ${giftCard.expired_date || 'N/A'}`),
                            confirmText: this.env._t('OK'),
                        });
                    }
                } catch (error) {
                    console.error('Error checking for gift cards:', error);
                }
            }

            // Call the original confirm method to complete the process
            super.confirm();
        }
    };

    // Register the extended component
    Registries.Component.extend(ClientListScreen, PosClientListScreenInherit);

    return PosClientListScreenInherit;
});