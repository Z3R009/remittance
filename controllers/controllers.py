# from odoo import http


# class Remittance(http.Controller):
#     @http.route('/remittance/remittance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/remittance/remittance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('remittance.listing', {
#             'root': '/remittance/remittance',
#             'objects': http.request.env['remittance.remittance'].search([]),
#         })

#     @http.route('/remittance/remittance/objects/<model("remittance.remittance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('remittance.object', {
#             'object': obj
#         })

