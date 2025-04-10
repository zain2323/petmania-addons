{
    "name": "Purchase Clearing Agents",
    "version": "15.0.0.0",
    "category": "Product",
    "author": "Zain Siddiqui",
    "license": "AGPL-3",
    "depends": ["purchase", "purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/cc_agent_view.xml",
        "views/ff_agent_view.xml",
        "views/purchase_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
