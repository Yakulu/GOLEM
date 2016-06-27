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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    nationality_id = fields.Many2one(default=_get_default_nationality_id)

    # Gender overwriting : no need for 'other' choice
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])


class GolemMember(models.Model):
    _name = 'golem.member'
    _description = 'GOLEM Member'
    _inherit = 'mail.thread'
    _inherits = {'res.partner': 'partner_id'}

    number = fields.Char('Number', size=50, index=True)
    pictures_agreement = fields.Boolean('Pictures agreement?')
    opt_out_sms = fields.Boolean('Out of SMS campaigns')
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
