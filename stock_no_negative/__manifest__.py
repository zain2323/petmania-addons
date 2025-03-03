# ?? 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Stock Disallow Negative",
    "version": "15.0.9",
    "category": "Inventory, Logistic, Storage",
    "license": "AGPL-3",
    "summary": "Disallow negative stock levels by default",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    'depends': ['stock', 'web', 'point_of_sale', 'bus'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_config_view.xml',
        "views/product_product_views.xml",
        "views/stock_location_views.xml"
    ],
    'assets': {
        'point_of_sale.assets': [
            'stock_no_negative/static/src/css/stock_qty.css',
            'stock_no_negative/static/src/js/models.js',
            'stock_no_negative/static/src/js/Chrome.js',
            'stock_no_negative/static/src/js/init.js',
            'stock_no_negative/static/src/js/db.js',
            'stock_no_negative/static/src/js/order_line.js',
            'stock_no_negative/static/src/js/ProductScreen.js',
            'stock_no_negative/static/src/js/ProductsWidget.js',
        ],
        'web.assets_qweb': [
            'stock_no_negative/static/src/xml/**/*',
        ],
    },
    "installable": True,
}
