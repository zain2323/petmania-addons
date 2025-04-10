{
    "name": "SCM Grading",
    "version": "15.0.0.2",
    "category": "Product",
    "author": "Zain Siddiqui",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_scm_grading_view.xml",
        "views/account_invoice_report_view.xml",
        "views/sale_report_view.xml",
        # "reports/sale_report_view.xml",
        # "reports/account_invoice_report_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
