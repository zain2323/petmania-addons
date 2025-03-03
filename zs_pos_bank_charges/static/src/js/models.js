odoo.define('zs_pos_bank_charges.models', function (require) {
    'use strict';
    const core = require('web.core');
    var models = require('point_of_sale.models');
    var PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    models.load_fields('pos.config', 'bank_charges_percent');
    models.load_fields('pos.config', 'bank_charges_product');

    const OrderSuper = models.Order.prototype;

    models.Order = models.Order.extend({
        add_bank_charges: function (total_amount) {
            var bank_charges_product = this.pos.db.get_product_by_id(this.pos.config.bank_charges_product[0]);
            if (!bank_charges_product) {return;}
            const order = this.pos.get_order();
            if (total_amount <= 0) {
                return;
            }
            const amount =  total_amount * (parseFloat(this.pos.config.bank_charges_percent) / 100)
            return this.add_product(bank_charges_product, {
                quantity: 1,
                price: amount,
                lst_price: amount,
            });
        },
    });


     const PaymentScreenExtend = PaymentScreenExtended => class extends PaymentScreen {

        addNewPaymentLine({ detail: paymentMethod }) {
           if (paymentMethod && paymentMethod.name === "Bank") {
               this.currentOrder.add_bank_charges(this.currentOrder.get_due());
           }
           return super.addNewPaymentLine({ detail: paymentMethod });
        }
     }

    // Register the custom component
    Registries.Component.extend(PaymentScreen, PaymentScreenExtend);

    return PaymentScreenExtend;
});
