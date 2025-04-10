# -*- coding: utf-8 -*-
{
    "name": "Odoo Advanced Search",
    "version": "15.0.1.4",
    "category": "Tools",
    'summary': """
Advanced Search, List view search,List View Manager, Global search, Quick Search, Listview search, Search engine, advance filter,Field Search,Tree view,document management, system,Resize column,Export Current View,Auto suggestion, Hide column, Show column,rename column,reorder Column, search expand,powerfull search, advance search,search list view, best search list, search list, search tree, tree search, tree view search,
search range, search by range, search by date, searchbar, web list search, search on list, easy search, fast search, Search for x2x, Search x2x, visible search, search filter, multi search, fastest search, base search, Voraussuche, Recherche Avancée, chercher, Søke, buscar, zoeken, поиск, dynamic search, speed up, micro search, seo, search view,domain filter, Code Search, Odoo Smart Search, Elastic search, dynamic list, speed search, Elasticsearch, Search Suggestion,search keyword, dynamic filter, product search, search autocomplete, auto search, automatic search, Configure Search, quick product search, optimize search, better search, Linear search, Binary search, Sequential Search, Interval Search, Interpolation search, search algorithm, Listview, 
listview manager, Odoo_advanced_search 
""",
    "description": """
        This module for odoo advance searching in list view., advance search odoo, search list view, list view search, advance search, search expand, powerfull search odoo, best search, best search list, search list, search tree, search, list search, tree search, tree view search, search range, search by range, search by date, searchbar, web list search, search on list, easy search, fast search, quick search, advanced search, Search for x2x, Search x2x, global search, search tool, filter, website search, search suggestion, visible search, search filter, multi search, fastest search, base search, Voraussuche, Recherche Avancée, chercher, Søke, buscar, zoeken, поиск, odoo 12 features, odoo search engine, odoo debrand, odoo branding, odoo rebrand, import order, import sale order, import account, database auto backup, database backup, signature, accounting report, export stock, document management system, dynamic list, dynamic search, product barcode, row number in list, biometric device integration, biometric integration, automatic workflow, professional report, speed up, all import, mipro search, odoo connector, import pricelist, import stock, integration, seo, pdf preview, checklist, manufacture, form builder, scan, invoice scan, audit, sale order report, import chart of account, odoo search filter, search view in odoo 11, odoo 10 search view, odoo domain filter, ODOO Code Search, Odoo Smart Search, Elastic search, dynamic list view, job costing, construction subcontract, construction management, work order odoo, material requision, backend theme, Construction app, Tracking Labor, Tracking,  Material, Tracking Overhead, Attendees, customer meeting, odoo calender, Project Report, tracking system, odoo timesheet, odoo mobile, mobile odoo, customer sign, digital signature, eSignature, document sign, document signature, contract signature, contract sign, odoo sign, iot, hw posbox, IoT Box, supply management, supply chain, website attendance, IoTBox Software, odoo new feature, overdue payment, calendar sync, import inventory, pdf report, Budget management, audit log, mass mail, mass email, access right, product lifecycle, product life cycle, speed search, excel report, quality control, bank transaction, barcode scan, mass editing, sales commission, sale commission, whatsapp, whats app, amazon, ebay, cdiscount, WooCommerce, Woo Commerce, shopify, financial report, inventory valuation, quickbook, promotion, appointment, BOOKING SOFTWARE, Clinic Management, pos receipt, product pack, project management, all in one, import image, import product image, import employee image, import customer image, import from file, import images from file, import product images, import customer images, import supplier images, import employee images, all in one import, import partner, Elasticsearch, Website Search Suggestion,search keyword, manufacturing, bom, bill of material, product configurator, gantt, connector, professional, dynamic filter, big data, product seach, sms notification, helpdesk, plm, business intelligence, business intelligence report, business report, upload image, gantt view, native, artificial intelligence, search autocomplete, auto search, automatic search, Configure Search, Magento,import all in one,quick product search, bulk,coupon, pos coupon,knowledge, remote backup, report designer, Dynamic Dashboard, optimize search, optimization, performance search, better search, Selection sort, Merge sort, Linear search, Binary search, Sequential Search, Interval Search, Interpolation search, search algorithm, Listview,  Advance Search, Advanced Search in ECommerce, Advanced Search for Tree View, Website Advanced Search, odoo advance search in tree view, Creating Advanced Search, Wildcard in advanced search, Advance Variant Level Product Search,ecommerce connector, e-commerce connector,marketplace connector, marketplace synchronization, portal document,List View advance search, ListView advance search,list view manager,listview manager, pdf export, excel export, Odoo_advanced_search, List View Manager
    """,
    "depends": ["web"],
    "price": 74.00,
    "currency": "USD",
    "data": [
             "views/res_users.xml",
            ],
    "assets": {
        'web.assets_backend': [
            '/odoo_advance_search/static/src/scss/search.scss',
            '/odoo_advance_search/static/src/js/search_view_common.js',
            '/odoo_advance_search/static/src/js/list_controller.js',
            '/odoo_advance_search/static/src/js/list_renderer.js'
        ],   
    },
    "images": ["static/description/OdooAdvanceSearch.png"],
    
    # Author
    'author': 'Synodica Solutions Pvt. Ltd.',
    'website': 'https://synodica.com',
    'maintainer': 'Synodica Solutions Pvt. Ltd.',
    
    'license': 'OPL-1',
    "installable": True,
    "auto_install": False,
    "application": True,
}

