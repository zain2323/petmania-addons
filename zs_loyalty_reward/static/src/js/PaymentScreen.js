odoo.define('zs_loyalty_reward.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');
    const rpc = require('web.rpc');

    const LoyaltyPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);

            }

            async _finalizeValidation() {
                const order = this.currentOrder;
                const client = order.get_client();
                console.log("client inside payment", client)
                if (client) {
                    const trackingData = await rpc.query({
                        model: 'customer.reward.tracking',
                        method: 'get_tracking_data',
                        args: [client.id],
                    });

                    console.log("tracking data", trackingData)

                    client.reward_tracking_data = trackingData;
                }

                super._finalizeValidation();
            }
        }

    Registries.Component.extend(PaymentScreen, LoyaltyPaymentScreen);

    return PaymentScreen;

});