# -*- coding: utf-8 -*-
{
    "name": "Product Brand Manager",
    "version": "15.0.4",
    "development_status": "Mature",
    "category": "Product",
    "summary": "Product Brand Manager",
    "author": "NetAndCo, Akretion, Prisnet Telecommunications SA, "
    "MONK Software, SerpentCS Pvt. Ltd., Tecnativa, Kaushal "
    "Prajapati, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/brand",
    "license": "AGPL-3",
    "depends": ["pos_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_brand_view.xml",
        "reports/sale_report_view.xml",
        "reports/account_invoice_report_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
