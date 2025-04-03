odoo.define('zs_pos_hide_paid_order.TicketScreenInherited', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const Ticket = TicketScreenInherited => class extends TicketScreen {

        _getFilterOptions() {
            const orderStates = this._getOrderStates();
            // orderStates.set('SYNCED', {text: this.env._t('Paid')});
            return orderStates;
        }

    };

    // Register the custom component
    Registries.Component.extend(TicketScreen, Ticket);

    return Ticket;
});
