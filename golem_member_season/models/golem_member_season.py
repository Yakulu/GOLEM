# -*- coding: utf-8 -*-

#    Copyright 2016 Fabien Bourgeois <fabien@yaltik.com>
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

from openerp import models, fields, api


class GolemMember(models.Model):
    _inherit = 'golem.member'

    season_ids = fields.Many2many('golem.season', string='Seasons')
    is_current = fields.Boolean('Current user?', store=True, default=False,
                                compute='_compute_is_current')

    @api.depends('season_ids')
    def _compute_is_current(self):
        """ Checks if member is active for current season """
        domain = [('is_default', '=', True)]
        default_season = self.env['golem.season'].search(domain)
        for member in self:
            member.is_current = default_season in member.season_ids


class GolemSeason(models.Model):

    @api.multi
    def write(self, values):
        """ Extends write to recomputes all current members in case of
        is_default changes and ensures that only one is_default is active """
        is_new_default = values.get('is_default')
        old_default_season = self.search([('is_default', '=', True)])
        res = super(GolemSeason, self).write(values)
        if is_new_default:
            if old_default_season:
                old_default_season.is_default = False
        self.env['golem.member'].search([])._compute_is_current()
        self.env['golem.activity'].search([])._compute_is_current()
        return res
