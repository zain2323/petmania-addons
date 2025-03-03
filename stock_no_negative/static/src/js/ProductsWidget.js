odoo.define('stock_no_negative.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	const DXLProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			mounted() {
				super.mounted();
				this.env.pos.on('change:is_sync', this.render, this);
			}
			willUnmount() {
				super.willUnmount();
				this.env.pos.off('change:is_sync', null, this);
			}

			_switchCategory(event) {
				this.env.pos.set("is_sync",true);
				super._switchCategory(event);
			}

			get is_sync() {
				return this.env.pos.get('is_sync');
			}

			get productsToDisplay() {
				let self = this;
				let prods = super.productsToDisplay;
				let prod_ids = [];
				$.each(prods, function( i, prd ){
					prod_ids.push(prd.id)
				});

				if (self.env.pos.config.restrict_out_of_stock) {
					this.rpc({
						model: 'stock.quant',
						method: 'get_qty_available',
						args: [self.env.pos.config.picking_type_id[0], prod_ids],
					}).then(function(output) {
						var prod_by_id = {};
						$.each(output, function(i, p_data){
							prod_by_id[p_data.product_id[0]] = p_data.available_quantity
						})
						self.env.pos.loc_onhand = prod_by_id;
						$.each(prods, function( i, prd ){
							var on_hand = 0.0;
							for(let key in prod_by_id){
								if(prd.id == key){
									on_hand = prod_by_id[key];
								}
							}
							self.env.pos.db.qty_by_product_id[prd.id] = on_hand;
						});
						self.env.pos.refresh_qty();
						self.env.pos.set("is_sync",false);
					});
				}
				return prods;
			}
		};

	Registries.Component.extend(ProductsWidget, DXLProductsWidget);

	return ProductsWidget;

});
