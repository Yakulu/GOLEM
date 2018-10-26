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

""" GOLEM Families Adaptations"""

from odoo import models, fields, api


class GolemFamily(models.Model):
    """ GOLEM Family Adaptations """
    _inherit = 'golem.family'

    family_history_ids = fields.One2many('golem.family.history', 'family_id',
                                         readonly=True, string='History details')

    @api.constrains('zip', 'city', 'country_id', 'member_ids')
    def save_family_history(self):
        """ Saves family history """
        default_season = self.env['golem.season'].search([('is_default', '=', True)], limit=1)
        for family in self:
            history_id = self.env['golem.family.history'].search([
                ('family_id', '=', family.id),
                ('season_id', '=', default_season.id)], limit=1)
            history_data = {
                'zip_code': family.zip,
                'city': family.city,
                'country_id': family.country_id.id,
                'member_ids':[(6, False, family.member_ids.ids)]
            }
            if history_id:
                history_id.write(history_data)
            else:
                history_data.update({'family_id': family.id,
                                     'season_id': default_season.id})
                self.env['golem.family.history'].create(history_data)
