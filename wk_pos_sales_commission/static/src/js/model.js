/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('wk_pos_sales_commission.models', function(require) {
    "use strict";
    var models = require('point_of_sale.models')
    var SuperOrder = models.Order.prototype;
    var SuperPosModel = models.PosModel.prototype;

    models.load_fields('res.users', ['is_commission_applicable'])
    models.load_fields('hr.employee', ['is_commission_applicable'])

    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            SuperOrder.initialize.call(this,attributes,options);
            this.is_commission = false;
            this.pos_config_id = null;
        },
        export_as_JSON: function() {
            var loaded=SuperOrder.export_as_JSON.call(this);
            if(this.pos.config.is_use_pos_commission){
                if(this.pos.config.show_apply_commission){
                    loaded.is_commission = this.is_commission;
                    loaded.pos_config_id = this.pos.config.id
                    return loaded
                }
                loaded.is_commission = true;
                loaded.pos_config_id = true
            }
            return loaded;
        },
    });
    models.PosModel = models.PosModel.extend({
        set_cashier: function(employee){
            var self = this;
            SuperPosModel.set_cashier.call(this,employee)
            if(!(employee.user_id && !employee.id)){
                _.each(this.employees, function(emp){
                    if(emp.id == employee.id){
                        if(emp.is_commission_applicable && self.config.is_use_pos_commission && self.config.show_apply_commission){
                            $("#apply_commission").show();
                        }
                        else{
                            $("#apply_commission").hide();
                        }
                    }
                })
            }
        },
    })
});