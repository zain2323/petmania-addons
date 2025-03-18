odoo.define('zs_customer_view_modification.ClientDetailsEditInherit', function(require) {
    'use strict';

    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const ClientDetailsEditInherit = (ClientDetailsEdit) =>
        class extends ClientDetailsEdit {
            saveChanges() {
                super.saveChanges();
                this.showPopup('ConfirmPopup', {
                    title: this.env._t('Success'),
                    body: this.env._t('Customer has been saved successfully!'),
                });
            }
        };

    Registries.Component.extend(ClientDetailsEdit, ClientDetailsEditInherit);

    return ClientDetailsEditInherit;
});
