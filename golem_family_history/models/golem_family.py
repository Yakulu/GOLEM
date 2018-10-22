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

from odoo import models, fields, api, _


class GolemFamily(models.Model):
    """ GOLEM Family Adaptations """
    _inherit = 'golem.family'

    family_history_ids = fields.One2many('golem.family.history', 'family_id')

    @api.constrains('city', 'country_id', 'member_ids')
    def save_family_history(self):
        """ save family history """
        default_season = self.env['golem.season'].search([('is_default', '=', True)])
        for family in self:
            history = self.env['golem.family.history'].search([
                ('family_id', '=', family.id),
                ('season_id', '=', default_season.id)])
            if history:
                history[0].write({
                    'city': family.city,
                    'country_id': family.country_id.id,
                    'member_ids':[(6, False, family.member_ids.ids)]
                    })
            else:
                self.env['golem.family.history'].create({
                    'family_id': family.id,
                    'season_id': default_season.id,
                    'city': family.city,
                    'country_id': family.country_id.id,
                    'member_ids':[(6, False, family.member_ids.ids)]
                    })
