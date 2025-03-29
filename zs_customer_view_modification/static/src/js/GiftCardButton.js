odoo.define("zs_customer_view_modification.GiftCardPopupExtended", function (require) {
    "use strict";

    const GiftCardPopup = require("pos_gift_card.GiftCardPopup");
    const Registries = require("point_of_sale.Registries");

    const GiftCardPopupExtended = (GiftCardPopup) =>
        class extends GiftCardPopup {
            async payWithGiftCard() {
                let giftCard = await this.getGiftCard();
                if (!giftCard) return;

                let gift =
                    this.env.pos.db.product_by_id[
                        this.env.pos.config.gift_card_product_id[0]
                        ];

                let currentOrder = this.env.pos.get_order();
                let orderProductIds = currentOrder.orderlines.models.map(line => line.product.id);
                console.log("product ids", orderProductIds)
                let lineUsed = await this.isGiftCardAlreadyUsed()
                if (lineUsed) currentOrder.remove_orderline(lineUsed);

                // apply the gift card where its applicable
                // Perform RPC to get applicable product IDs
                let applicableProductIds = await this.rpc({
                    model: "gift.card",
                    method: "get_applicable_products",
                    args: [[giftCard.id]],
                });

                if (applicableProductIds) {
                    let invalidProducts = orderProductIds.filter(id => !applicableProductIds.includes(id));
                    if (invalidProducts.length > 0) {
                        await this.showPopup("ErrorPopup", {
                            title: "Invalid Product",
                            body: "One or more products in the order cannot be paid using this gift card.",
                        });
                        return;
                    }
                }
                currentOrder.add_product(gift, {
                    price: this.getPriceToRemove(giftCard),
                    quantity: 1,
                    merge: false,
                    gift_card_id: giftCard.id,
                });

                this.cancel();
            }
        };

    Registries.Component.extend(GiftCardPopup, GiftCardPopupExtended);

    return GiftCardPopupExtended;
});
