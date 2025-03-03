odoo.define('stock_no_negative.productScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const DXLProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
				this.env.pos.qty_sync(Object.keys(this.env.pos.db.product_by_id).map(Number));
				this.env.pos.refresh_qty();
			}
			async _onClickPay() {
				super._onClickPay();
			}
		};

	Registries.Component.extend(ProductScreen, DXLProductScreen);

	return ProductScreen;

});
