odoo.define('zs_pos_cash_out_modifications.pos_cash_move', function (require) {
    'use strict';

    const CashMoveButton = require('point_of_sale.CashMoveButton');
    const Registries = require('point_of_sale.Registries');
    const {_t} = require('web.core');

    const TRANSLATED_CASH_MOVE_TYPE = {
        in: _t('in'),
        out: _t('out'),
    };

    const CustomCashMoveButton = (CashMoveButton) => class extends CashMoveButton {
        async onClick() {
            const {confirmed, payload} = await this.showPopup('CashMovePopup');
            if (!confirmed) return;
            const {type, amount, reason} = payload;
            const translatedType = TRANSLATED_CASH_MOVE_TYPE[type];
            const formattedAmount = this.env.pos.format_currency(amount);
            if (!amount) {
                return this.showNotification(
                    _.str.sprintf(this.env._t('Cash in/out of %s is ignored.'), formattedAmount),
                    3000
                );
            }
            const extras = {formattedAmount, translatedType};
            await this.rpc({
                model: 'pos.session',
                method: 'try_cash_in_out',
                args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
            });
            if (this.env.pos.proxy.printer) {
                const renderedReceipt = this.env.qweb.renderToString('point_of_sale.CashMoveReceipt', {
                    _receipt: this._getReceiptInfo({...payload, translatedType, formattedAmount}),
                });
                const printResult = await this.env.pos.proxy.printer.print_receipt(renderedReceipt);
                if (!printResult.successful) {
                    this.showPopup('ErrorPopup', {title: printResult.message.title, body: printResult.message.body});
                }
            }
            this.showNotification(
                _.str.sprintf(this.env._t('Successfully made a cash %s of %s.'), type, formattedAmount),
                3000
            );
            if (type === "out") {
                this.env.pos.cashed_out = true;
            }
        }
    };

    Registries.Component.extend(CashMoveButton, CustomCashMoveButton);

    return CustomCashMoveButton;
});
