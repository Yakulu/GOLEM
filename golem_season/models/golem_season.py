# -*- coding: utf-8 -*-

#    Copyright 2016-2018 Fabien Bourgeois <fabien@yaltik.com>
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
from odoo.exceptions import ValidationError

class GolemSeason(models.Model):
    """ GOLEM Season """
    _name = 'golem.season'
    _description = 'GOLEM Season'
    _order = 'date_start desc'
    _sql_constraints = [('golem_season_name_uniq', 'UNIQUE (name)',
                         _('This season name has already been used.'))]

    name = fields.Char('Season name', copy=False, required=True)
    membership_ids = fields.One2many('product.template', 'membership_season_id',
                                     string='Membership types',
                                     domain=[('membership', '=', True)])
    member_counter = fields.Integer('Counter for member number generation',
                                    readonly=True, default=1)
    date_start = fields.Date('Period start')
    date_end = fields.Date('Period end')
    is_default = fields.Boolean('Default season for views?', readonly=True)

    @api.onchange('membership_ids')
    def _onchange_season_dates(self):
        """ Sets defaults dates according to membership type """
        for season in self:
            if season.membership_ids and not season.date_start:
                season.update({
                    'date_start': season.membership_ids[0].membership_date_from,
                    'date_end': season.membership_ids[0].membership_date_to
                })

    @api.constrains('date_start', 'date_end')
    def _check_period(self):
        """ Check if end date if after start date and if there is no conflict
        with existing periods """
        for season in self:
            if season.date_start or season.date_end:
                if season.date_start and not season.date_end:
                    raise ValidationError(_('The date end is required'))
                elif season.date_end and not season.date_start:
                    raise ValidationError(_('The date start is required'))
                if season.date_start > season.date_end:
                    raise ValidationError(_('Start of the period cannot be '
                                            'after end of the period.'))
                seasons = self.env['golem.season'].search([])
                for eachs in seasons:
                    if eachs.date_start < season.date_start < eachs.date_end:
                        msg = _(u'Start of the period is in range of an '
                                'existing period.')
                        raise ValidationError(msg)
                    if eachs.date_start < season.date_end < eachs.date_end:
                        msg = _(u'End of the period is in range of an '
                                'existing period.')
                        raise ValidationError(msg)
                    if season.date_start < eachs.date_start < season.date_end:
                        msg = _(u'Current period cannot be included into '
                                'another existing period.')
                        raise ValidationError(msg)

    @api.multi
    def do_default_season(self):
        """ is_default on and ensure that only one is_default is active """
        self.ensure_one()
        old_default_season = self.search([('is_default', '=', True)])
        if old_default_season:
            old_default_season.is_default = False
        self.is_default = True

    @api.model
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
                raise ValidationError(emsg)
            else:
                return super(GolemSeason, self).unlink()
