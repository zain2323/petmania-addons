# -*- coding: utf-8 -*-
# from odoo import http


# class DxlPrintNtnStrnV15(http.Controller):
#     @http.route('/dxl_print_ntn_strn_v15/dxl_print_ntn_strn_v15', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dxl_print_ntn_strn_v15/dxl_print_ntn_strn_v15/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dxl_print_ntn_strn_v15.listing', {
#             'root': '/dxl_print_ntn_strn_v15/dxl_print_ntn_strn_v15',
#             'objects': http.request.env['dxl_print_ntn_strn_v15.dxl_print_ntn_strn_v15'].search([]),
#         })

#     @http.route('/dxl_print_ntn_strn_v15/dxl_print_ntn_strn_v15/objects/<model("dxl_print_ntn_strn_v15.dxl_print_ntn_strn_v15"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dxl_print_ntn_strn_v15.object', {
#             'object': obj
#         })
