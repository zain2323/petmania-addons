odoo.define('dxl_closing_control_restriction.models', function (require) {
"use strict";

var models = require('point_of_sale.models');

models.load_fields("pos.config", "group_closing_control_restriction"); 

var posmodel_super = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    after_load_server_data: function() {
        return posmodel_super.after_load_server_data.apply(this, arguments).then(() => { 
        	var self = this
        	self.user.group_closing_control_restriction = 'False';
        	self.user.groups_id.some(function(group_id) {
                if (group_id === self.config.group_closing_control_restriction[0]) {
                	self.user.group_closing_control_restriction = 'True';
                }
            });
        });
    },
});

});
