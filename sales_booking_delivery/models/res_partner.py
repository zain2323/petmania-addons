# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        return [(partner.id, '%s%s' % (partner.phone and '[%s] ' % partner.phone or '', partner._get_name())) for partner in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name and not self.env.context.get('import_file'):
            args = args if args else []
            args.extend(['|', ['phone', 'ilike', name],
                         '|', ['mobile', 'ilike', name],
                         '|', ['name', 'ilike', name],
                         '|', ['email', 'ilike', name],
                         ['function', 'ilike', name]])
            name = ''
        return super(ResPartner, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
