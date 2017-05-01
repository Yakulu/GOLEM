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

""" GOLEM Season management """

from odoo import models, fields, api, _

class GolemSeason(models.Model):
    """ GOLEM Season """
    _name = 'golem.season'
    _description = 'GOLEM Season'
    _order = 'date_start desc'
    _sql_constraints = [('golem_season_name_uniq', 'UNIQUE (name)',
                         _('This season name has already been used.'))]

    name = fields.Char('Season name', copy=False)
    member_counter = fields.Integer('Counter for member number generation',
                                    readonly=True, default=0)
    date_start = fields.Date('Period start')
    date_end = fields.Date('Period end')

    @api.constrains('date_start', 'date_end')
    def _check_period(self):
        """ Check if end date if after start date and if there is no conflict
        with existing periods """
        for season in self:
            if season.date_start > season.date_end:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))
            else:
                seasons = self.env['golem.season'].search([])
                for eachs in seasons:
                    if eachs.date_start < season.date_start < eachs.date_end:
                        msg = _(u'Start of the period is in range of an '
                                'existing period.')
                        raise models.ValidationError(msg)
                    if eachs.date_start < season.date_end < eachs.date_end:
                        msg = _(u'End of the period is in range of an '
                                'existing period.')
                        raise models.ValidationError(msg)
                    if season.date_start < eachs.date_start < season.date_end:
                        msg = _(u'Current period cannot be included into '
                                'another existing period.')
                        raise models.ValidationError(msg)

    is_default = fields.Boolean('Default season for views?', readonly=True)

    @api.multi
    def do_default_season(self):
        """ is_default on and ensure that only one is_default is active. Also
        recomputes is_current for members and activities. For simplicity use a
        magic trick around registry rather than double inheritance """
        self.ensure_one()
        old_default_season = self.search([('is_default', '=', True)])
        if old_default_season:
            old_default_season.is_default = False
        self.is_default = True
        if 'golem.member' in self.env.registry:
            all_members = self.env['golem.member'].search([])
            all_members.compute_is_current()
            all_members.generate_number()
        if 'golem.activity' in self.env.registry:
            self.env['golem.activity'].search([]).compute_is_current()

    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, values):
        """ If the season if the first one created, it must be by default """
        if self.search_count([]) == 0:
            values['is_default'] = True
        return super(GolemSeason, self).create(values)

    @api.multi
    def unlink(self):
        """ Forbids default season removal """
        for season in self:
            if season.is_default:
                emsg = _('You can\'t delete the default season')
                raise models.ValidationError(emsg)
            else:
                return super(GolemSeason, self).unlink()
