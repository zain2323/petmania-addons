odoo.define('your_module.CompanyStageSystray', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');


    console.log("systray loading")

    var CompanyStageSystray = Widget.extend({
        template: 'CompanyStageSystray',
        events: {
            'click': '_onClick',
        },
        start: function () {
            var self = this;
            const currentCompanyId = session.user_context.allowed_company_ids[0];
            const currentCompany = session.user_companies.allowed_companies[currentCompanyId];
            rpc.query({
                model: 'res.company',
                method: 'search_read',
                args: [[['id', '=', currentCompany.id]], ['stage']],
            }).then(function (result) {
                if (result.length) {
                    self.$('.o_company_stage').text(result[0].stage);
                }
            });
        },
        _onClick: function () {
            alert("Current Company Stage: " + this.$('.o_company_stage').text());
        }
    });

    SystrayMenu.Items.push(CompanyStageSystray);
    return CompanyStageSystray;
});
