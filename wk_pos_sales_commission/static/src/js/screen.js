/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('wk_pos_sales_commission.screen', function(require) {
    "use strict";
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');

    // ApplyCommissionButton Popup
	class ApplyCommissionButton extends PosComponent {
        async onClick() {
            var self = this;
            var order = self.env.pos.get_order();
            if(order.is_commission){
                order.is_commission = false
                self.showScreen('ClientListScreen');
                self.showScreen('ProductScreen');
                $('#apply_commission').removeClass('commission_selected')
            }
            else{
                order.is_commission = true
                self.showScreen('ClientListScreen');
                self.showScreen('ProductScreen');
                $('#apply_commission').addClass('commission_selected')
            }
        }
        constructor() {
            super(...arguments);
			var self = this;
            useListener('click', self.onClick);
            var order = self.env.pos.get_order();
			setTimeout(function(){
                if(self.env.pos.get_cashier().is_commission_applicable){
                    $("#apply_commission").show();
                    if(self.env.pos.get_order().is_commission){
                        $('#apply_commission').addClass('commission_selected')
                    }
                    else{
                        $('#apply_commission').removeClass('commission_selected')
                    }
                }
                else{
                    if(self.env.pos.user.is_commission_applicable && self.env.pos.config.is_use_pos_commission && self.env.pos.config.show_apply_commission){
                        $("#apply_commission").show();
                    }
                    else{
                        $("#apply_commission").hide();
                        order.is_commission = false
                    } 
                }
            }, 100);
        }
    }
    ApplyCommissionButton.template = 'ApplyCommissionButton';
    ProductScreen.addControlButton({ component: ApplyCommissionButton, condition: function() {
        var show = false
        if(this.env.pos.config.is_use_pos_commission){
            if(this.env.pos.config.show_apply_commission){
                if(this.env.pos.config.module_pos_hr){
                    show = true
                }
                else{
                    if(this.env.pos.user.is_commission_applicable){
                        show = true
                    }
                }
            }
        }
        return show; 
    },});
	Registries.Component.add(ApplyCommissionButton);
});
