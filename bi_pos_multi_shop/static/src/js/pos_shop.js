odoo.define('bi_pos_multi_shop.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var PosDB = require('point_of_sale.DB');
	var rpc = require('web.rpc');
	var _t = core._t;
	var QWeb = core.qweb;
	var shop_ref_id;
	var current_shop;
	var curr_shop;
	var exports = {};

	models.load_models({
		model: 'pos.config',
		fields: ['shop_id'],
		domain: [],
		loaded: function(self, pos_config_shops){
			curr_shop = self.config.shop_id[0]
			self.db.pos_config_shops = pos_config_shops;
		},
	});

	models.load_models({
		model:  'product.product',
		fields: ['display_name', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
				 'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
				 'product_tmpl_id','tracking'],
		order:  _.map(['sequence','default_code','name'], function (name) { return {name: name}; }),
		domain: function(self){
			var domain = ['&', '&', ['sale_ok','=',true],['available_in_pos','=',true],'|',['company_id','=',self.config.company_id[0]],['company_id','=',false]];
			if( self.config.shop_id && self.config.shop_id[0]){
				var shop = self.config.shop_id[0];
				domain.unshift('&');
				domain.push(['shop_ids','in',[shop]]);
			}
			if (self.config.limit_categories &&  self.config.iface_available_categ_ids.length) {
				domain.unshift('&');
				domain.push(['pos_categ_id', 'in', self.config.iface_available_categ_ids]);
			}
			if (self.config.iface_tipproduct){
			  domain.unshift(['id', '=', self.config.tip_product_id[0]]);
			  domain.unshift('|');
			}
			return domain;
		},
		context: function(self){ return { display_default_code: false }; },
		loaded: function(self, products){
			var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
			var conversion_rate = self.currency.rate / self.company_currency.rate;
			self.db.product_by_id = {};
			self.db.product_by_barcode = {};
			self.db.product_by_category_id = {};
			self.db.add_products(_.map(products, function (product) {
				if (!using_company_currency) {
					product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
				}
				product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
				return new models.Product({}, product);
			}));
		},
	});



	models.load_models({
		model: 'pos.multi.shop',
		fields: ['name', 'image', 'config_id','stock_location_id','picking_type_id', 'related_partner_id', 'product_ids', 'street', 'street2', 'city', 'zip', 'state_id', 'country_id', 'website', 'phone', 'email'],
		domain: [],
		loaded: function(self, pos_shops){
			 self.pos_shops = pos_shops;
		},
	});
 
});
