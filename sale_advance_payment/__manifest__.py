# -*- coding: utf-8 -*-

{
    "name": "Sale Advance Payment",
    "version": "15.0.0",
    "category": "Sales",
    "summary": """Sale Advance Payment""",
    "description": """Sale Advance Payment""",
    "depends": ["sale_management"],
    "data": [   "security/ir.model.access.csv",
                "security/button_security.xml",
                "wizard/sale_advance_payment_wzd_view.xml",
                "views/sale_view.xml",
             ],
    "installable": True,
    "application": True,
}
