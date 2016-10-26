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


class GolemActivity(models.Model):
    _name = 'golem.activity'
    _description = 'GOLEM Activity'
    _inherit = 'mail.thread'
    _inherits = {'product.template': 'product_id'}
    _rec_name = 'full_name'

    product_id = fields.Many2one('product.template', required=True,
                                 ondelete='cascade')

    image = fields.Binary(help='This field holds the image used as image for '
                          'the activity.')

    full_name = fields.Char('Name', compute='_compute_full_name', store=True,
                            index=True)

    @api.one
    @api.depends('name', 'default_code')
    def _compute_full_name(self):
        """ Provide a better displayed name """
        full_name = unicode(self.name)
        if self.default_code:
            full_name = u'[{}] {}'.format(self.default_code, full_name)
        self.full_name = full_name

    type_of = fields.Selection([('activity', _('Activity')),
                                ('workshop', _('Workshop')),
                                ('training', _('Training'))],
                               default='activity', index=True, string='Type')

    @api.onchange('type_of')
    def onchange_type_of(self):
        for s in self:
            if s.type_of != 'activity':
                s.is_recurrent = False
            else:
                s.is_recurrent = True

    # TODO: to link with calendar.event

    @api.model
    def _default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain)

    season_id = fields.Many2one('golem.season', string='Season', copy=False,
                                required=True, default=_default_season,
                                ondelete='restrict')

    is_current = fields.Boolean('Current season?', store=True, default=False,
                                compute='_compute_is_current')

    @api.one
    @api.depends('season_id')
    def _compute_is_current(self):
        """ Checks if activity is active for current season """
        default_season = self._default_season()
        self.is_current = (default_season == self.season_id)

    animator_id = fields.Many2one('res.partner', string='Animator',
                                  domain=[('is_company', '=', False)])
    categ_id = fields.Many2one('product.category',
                               help='Select category for the current activity')
    is_recurrent = fields.Boolean('Is recurrent ?', default=True,
                                  help='Work in progress')
    date_start = fields.Date('Start date', copy=False)
    date_stop = fields.Date('End date', copy=False)

    @api.onchange('date_start')
    def onchange_date_start(self):
        """ Sets end date to start date if no start date """
        for s in self:
            if not s.date_stop:
                s.date_stop = s.date_start

    @api.constrains('date_start', 'date_stop')
    def _check_period(self):
        """ Check if end date if after start date """
        for a in self:
            if a.date_start and a.date_stop and a.date_start > a.date_stop:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))

    @api.onchange('season_id')
    def onchange_season_dates(self):
        """ Sets defaults dates according to season """
        for a in self:
            if a.season_id:
                if not a.date_start:
                    a.date_start = a.season_id.date_start
                if not a.date_stop:
                    a.date_stop = a.season_id.date_end

    weekday = fields.Selection([('mon', _('Monday')),
                                ('tue', _('Tuesday')),
                                ('wed', _('Wednesday')),
                                ('thu', _('Thursday')),
                                ('fri', _('Friday')),
                                ('sat', _('Saturday')),
                                ('sun', _('Sunday'))], copy=False)
    hour_start = fields.Float('Start time', copy=False)
    hour_stop = fields.Float('Stop time', copy=False)

    @api.onchange('hour_start')
    def onchange_hour_start(self):
        """ Sets end hour to start hour if no start hour """
        for s in self:
            if s.hour_start and not s.hour_stop:
                s.hour_stop = s.hour_start + 1

    @api.constrains('hour_start', 'hour_stop')
    def _check_hour_period(self):
        """ Check if end hour if after start hour """
        for s in self:
            if s.hour_start > s.hour_stop:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Make default service for type
    type = fields.Selection(default='service')
    # Copy the default code
    default_code = fields.Char(copy=True)
