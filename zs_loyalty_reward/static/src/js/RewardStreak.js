odoo.define('zs_loyalty_reward.RewardStreakButton', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');
    const {useState} = owl.hooks;

    class RewardStreakButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        checkButtonStatus() {
            console.log("just returning")
            return true
            // const order = this.env.pos.get_order();
            // console.log("here")
            // const partner = order.get_client();
            // if (!partner) {
            //     return false;
            // }
            // const orderLines = order.get_orderlines();
            // const productIds = [...new Set(orderLines.map(line => line.product.id))];
            //
            // try {
            //     const rewardConfigs = await this.rpc({
            //         model: 'loyalty.reward.config',
            //         method: 'search_read',
            //         args: [
            //             [['product_id', 'in', productIds]],
            //             ['product_id', 'purchase_count']
            //         ]
            //     });
            //     console.log("config", rewardConfigs)
            //     if (rewardConfigs && rewardConfigs.length > 0) {
            //         const config = rewardConfigs[0]
            //         console.log("final config", config)
            //         const hasStreak = await this.rpc({
            //             model: 'loyalty.reward.config',
            //             method: 'check_streak',
            //             args: [config.id, partner.id]
            //         });
            //         console.log("has_streak", hasStreak)
            //         return hasStreak
            //     }
            //     return false
            // } catch (error) {
            //     console.error('Error checking streak status:', error);
            //     return false
            // }
        }

        async onClick() {
            const order = this.env.pos.get_order();
            const partner = order.get_client();

            if (!partner) {
                Gui.showPopup('ErrorPopup', {
                    title: this.env._t('No Customer Selected'),
                    body: this.env._t('Please select a customer first.')
                });
                return;
            }

            try {
                // Get all unique products in the current order
                const orderLines = order.get_orderlines();
                const productIds = [...new Set(orderLines.map(line => line.product.id))];

                // Search for reward configurations for these products
                const rewardConfigs = await this.rpc({
                    model: 'loyalty.reward.config',
                    method: 'search_read',
                    args: [
                        [['product_id', 'in', productIds]],
                        ['product_id', 'purchase_count', 'validity_days']
                    ]
                });
                // If no reward configs found, show message
                if (rewardConfigs.length === 0) {
                    Gui.showPopup('ErrorPopup', {
                        title: this.env._t('No Rewards'),
                        body: this.env._t('No reward configurations found for the products in this order.')
                    });
                    return;
                }

                // Check streak for each reward configuration
                for (let config of rewardConfigs) {
                    const result = await this.rpc({
                        model: 'loyalty.reward.config',
                        method: 'check_reward_streak',
                        args: [config.id, partner.id]
                    });

                    if (result) {
                        // Result is the product to be added
                        const product = await this.env.pos.db.get_product_by_id(result.product_id);

                        if (product) {
                            // Add the free product to the order
                            order.add_product(product, {
                                quantity: 1,
                                merge: false,
                                extras: {
                                    is_reward: true
                                }
                            });
                            order.get_last_orderline().set_discount(99.99)

                            // Show success popup
                            Gui.showPopup('ConfirmPopup', {
                                title: this.env._t('Reward Earned!'),
                                body: this.env._t(`Congratulations! You've earned a free ${product.display_name}`)
                            });

                            // Break after first reward
                            break;
                        }
                    }
                }
            } catch (error) {
                Gui.showPopup('ErrorPopup', {
                    title: this.env._t('Error'),
                    body: this.env._t('Could not check reward streak.')
                });
                console.error(error);
            }
        }
    }

    RewardStreakButton.template = 'RewardStreakButton';

    ProductScreen.addControlButton({
        component: RewardStreakButton,
        condition: function () {
            return true; // or some specific condition
        },
    });

    Registries.Component.add(RewardStreakButton);

    return RewardStreakButton;
});