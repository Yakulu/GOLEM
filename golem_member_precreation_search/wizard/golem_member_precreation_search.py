# -*- coding: utf-8 -*-

#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" GOLEM Precreation Member Request wizard"""

from odoo import models, fields, api

class GolemPrecreationMemberRequestWizard(models.TransientModel):
    """GOLEM Precreation Request Member Wizard """
    _name = "golem.precreation.member.request.wizard"

    name = fields.Char()
    is_member = fields.Boolean()

    @api.multi
    def search_members(self):
        """ Search members """
        self.ensure_one()
        model = self._context.get('model')
        domain = ['|',
                  ('name', 'ilike', self.name),
                  ('email', 'ilike', self.name)]
        members = self.env[model].search(domain)
        ids = []
        if members:
            ids = members.mapped('id')
        title = ""
        context = {}
        if self.is_member:
            title = 'Member search result "{}"'.format(self.name)
            context = {'default_member_ids': ids}
        else:
            title = 'Contact search result "{}"'.format(self.name)
            context = {'default_contact_ids': ids}

        return {'name' : (title),
                'type' : 'ir.actions.act_window',
                'res_model' : 'golem.precreation.member.result.wizard',
                'context': context,
                'view_mode': 'form',
                'flags': {'initial_mode': 'view'},
                'target': 'new'}
