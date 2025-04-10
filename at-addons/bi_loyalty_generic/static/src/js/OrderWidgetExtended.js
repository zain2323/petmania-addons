odoo.define('bi_loyalty_generic.OrderWidgetExtended', function(require){
	'use strict';

	const OrderWidget = require('point_of_sale.OrderWidget');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { Component } = owl;

	const OrderWidgetExtended = (OrderWidget) =>
		class extends OrderWidget {
			constructor() {
				super(...arguments);
			}
			
			get loyalty_pts(){
				let order = this.env.pos.get_order();
				let loyalty_pts = order ? order.get_total_loyalty() : 0;
				return loyalty_pts;
			}

			get temp_loyalty_point(){
				let order = this.env.pos.get_order();
				let partner = order.get_client();
				let loyalty_pts = order ? order.get_total_loyalty() : 0;
				let temp_loyalty_point = 0

				if(partner){
					temp_loyalty_point = partner.loyalty_pts
				}
				
				if(this.env.pos.pos_loyalty_setting.length != 0)
				{
					if (partner) {
						if(order.get('remove_true') == true)
						{
							partner.loyalty_pts = partner.loyalty_pts
							order.set('update_after_redeem',partner.loyalty_pts)
						}
						else{
							if(order.get('update_after_redeem') >= 0){
								partner.loyalty_pts = order.get("update_after_redeem");
							}else{
								partner.loyalty_pts = partner.loyalty_pts
							}
						}					
						temp_loyalty_point = partner.loyalty_pts + loyalty_pts ;				
					}
				}
				return temp_loyalty_point;
			}
		};

	Registries.Component.extend(OrderWidget, OrderWidgetExtended);

	return OrderWidget;

});