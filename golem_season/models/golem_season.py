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

from openerp import models, fields, api, _


class GolemSeason(models.Model):
    """ GOLEM Season """
    _name = 'golem.season'
    _description = 'GOLEM Season'
    _order = 'date_start desc'

    name = fields.Char('Season name')
    member_counter = fields.Integer('Counter for member number generation',
                                    readonly=True, default=0)
    date_start = fields.Date('Period start')
    date_end = fields.Date('Period end')
    is_default = fields.Boolean('Default season for views?')

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
                for s in seasons:
                    if s.date_start < season.date_start < s.date_end:
                        msg = _('Start of the period is in range of an '
                                'existing period {}'.format(s.name))
                        raise models.ValidationError(msg)
                    if s.date_start < season.date_end < s.date_end:
                        msg = _('End of the period is in range of an '
                                'existing period {}'.format(s.name))
                        raise models.ValidationError(msg)
                    if season.date_start < s.date_start < season.date_end:
                        msg = _('Period {} cannot be included into current '
                                'period'.format(s.name))
                        raise models.ValidationError(msg)

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
            self.env['golem.member'].search([])._compute_number()
            self.env['golem.activity'].search([])._compute_is_current()
        return res
