odoo.define("stock_no_negative.chrome", function (require) {
    "use strict";

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require("point_of_sale.Registries");
    var bus_service = require("bus.BusService");
    const bus = require("bus.Longpolling");
    const session = require("web.session");
    var rpc = require("web.rpc");
    var core = require("web.core");
    var DB = require("point_of_sale.DB");
    var models = require("point_of_sale.models");

    var _t = core._t;

    const PosResChrome = (Chrome) =>
        class extends Chrome {
            async start() {
                await super.start();
                await this._poolData(); 
            }
            _poolData(){
                this.env.services['bus_service'].updateOption('stock.update',session.uid);
                this.env.services['bus_service'].onNotification(this,this._onNotification);
                this.env.services['bus_service'].startPolling();
            }
            _onNotification(notifications) {
                console.log('FIRE..............', notifications)
                var stock_quant = notifications.filter(function (item) {
                    return item.type === "stock_update";
                }).map(function (item) {
                    return item.payload;
                });
                var flat_stock_quant = _.reduceRight(stock_quant, function (a, b) {
                    return a.concat(b)
                }, []);
                this.env.pos.on_stock_notification(flat_stock_quant);
            }
        };

    Registries.Component.extend(Chrome, PosResChrome);

    return Chrome;
});
