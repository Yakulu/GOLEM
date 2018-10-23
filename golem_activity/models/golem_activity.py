# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM activities related models """

import logging
from odoo import models, fields, api, _
_LOGGER = logging.getLogger(__name__)

class GolemActivityType(models.Model):
    """ GOLEM Activity Type """
    _name = 'golem.activity.type'
    _description = 'GOLEM Activity Type'

    _sql_constraints = [('golem_activity_type_name_uniq', 'UNIQUE (name)',
                         _('This activity type name has already been used.'))]

    name = fields.Char('Activity type', required=True, translate=True)
    is_recurrent = fields.Boolean('Is recurrent?')


class GolemActivityAudience(models.Model):
    """ GOLEM Activity Audience """
    _name = 'golem.activity.audience'
    _description = 'GOLEM Activity Audience'

    _sql_constraints = [('golem_activity_audience_name_uniq', 'UNIQUE (name)',
                         _('This activity audience name has already been used.'))]

    name = fields.Char('Activity audience', required=True, translate=True)


class GolemActivity(models.Model):
    """ GOLEM Activity """
    _name = 'golem.activity'
    _description = 'GOLEM Activity'
    _inherit = 'mail.thread'
    _inherits = {'product.template': 'product_id'}
    _order = 'default_code, name, id'
    _rec_name = 'full_name'

    product_id = fields.Many2one('product.template', required=True,
                                 ondelete='cascade')

    image = fields.Binary(help='This field holds the image used as image for '
                          'the activity.')

    full_name = fields.Char('Name', compute='_compute_full_name', store=True,
                            index=True)
    is_fullseason = fields.Boolean('Is full season?',
                                   compute='_compute_is_full_season')
    location = fields.Char()
    audience_id = fields.Many2one('golem.activity.audience', string='Audience',
                                  index=True, auto_join=True)

    @api.onchange('is_fullseason')
    def onchange_fullseason(self):
        """ Sets dates as season ones if needed """
        for activity in self:
            if activity.is_fullseason:
                if activity.season_id.date_start:
                    activity.date_start = activity.season_id.date_start
                if activity.season_id.date_end:
                    activity.date_stop = activity.season_id.date_end

    @api.depends('date_start', 'date_stop')
    def _compute_is_full_season(self):
        """ Display date for is full season """
        for activity in self:
            if activity.date_start == activity.season_id.date_start and \
               activity.date_stop == activity.season_id.date_end:
                activity.is_fullseason = True

    @api.depends('name', 'default_code')
    def _compute_full_name(self):
        """ Provide a better displayed name """
        for activity in self:
            full_name = unicode(activity.name)
            if activity.default_code:
                full_name = u'[{}] {}'.format(activity.default_code, full_name)
            activity.full_name = full_name

    @api.model
    def default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain)

    season_id = fields.Many2one('golem.season', string='Season', copy=False,
                                required=True, default=default_season,
                                index=True, auto_join=True,
                                ondelete='restrict')
    is_default = fields.Boolean('Default season?',
                                compute='_compute_is_default',
                                search='_search_is_default')

    @api.depends('season_id')
    def _compute_is_default(self):
        """ Checks if activity is active for default season """
        default_season = self.default_season()
        for activity in self:
            activity.is_default = (default_season == activity.season_id)

    @api.multi
    def _search_is_default(self, operator, value):
        """ Search function for is default """
        if operator in ('in', '='):
            operator = '=' if value else '!='
        elif operator in ('not in', '!='):
            operator = '!=' if value else '='
        else:
            err = _('Unsupported operator for defautl season search')
            raise NotImplementedError(err)
        return [('season_id', operator, self.default_season().id)]

    animator_id = fields.Many2one('res.partner', string='Animator',
                                  index=True, auto_join=True,
                                  domain=[('is_company', '=', False)])
    type_id = fields.Many2one('golem.activity.type', required=True, index=True,
                              auto_join=True, string='Type')
    is_recurrent = fields.Boolean(related='type_id.is_recurrent')
    date_start = fields.Date('Start date', copy=False)
    date_stop = fields.Date('End date', copy=False)

    @api.constrains('animator_id')
    def save_animator_id(self):
        """ Enabling is_animator flag """
        for activity in self:
            activity.animator_id.is_animator = True


    @api.onchange('date_start')
    def _onchange_date_start(self):
        """ Sets end date to start date if no start date """
        for activity in self:
            if not activity.date_stop:
                activity.date_stop = activity.date_start

    @api.constrains('date_start', 'date_stop')
    def _check_period(self):
        """ Checks if end date if after start date """
        for activity in self:
            season = activity.season_id
            if activity.date_start and activity.date_stop and \
                    activity.date_start > activity.date_stop:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))
            if season.date_start and season.date_start > activity.date_start:
                msg = _(u'Activity start date can not be set before '
                        'linked season start.')
                raise models.ValidationError(msg)
            if season.date_end and season.date_end < activity.date_stop:
                msg = _(u'Activity end date can not be set after '
                        'linked season end.')
                raise models.ValidationError(msg)

    @api.onchange('season_id')
    def _onchange_season_dates(self):
        """ Sets defaults dates according to season """
        for activity in self:
            if activity.season_id:
                if not activity.date_start:
                    activity.date_start = activity.season_id.date_start
                if not activity.date_stop:
                    activity.date_stop = activity.season_id.date_end

    weekday = fields.Selection([('mon', _('Monday')),
                                ('tue', _('Tuesday')),
                                ('wed', _('Wednesday')),
                                ('thu', _('Thursday')),
                                ('fri', _('Friday')),
                                ('sat', _('Saturday')),
                                ('sun', _('Sunday'))], copy=False)
    hour_start = fields.Float('Start time', copy=False)
    hour_stop = fields.Float('Stop time', copy=False)
    hour_start_display = fields.Char('Hour start',
                                     compute='_compute_hour_start_display')

    @api.depends('hour_start')
    def _compute_hour_start_display(self):
        """ Computes datetime from day hour start """
        for activity in self:
            activity.hour_start_display = (activity.hour_start if
                                           activity.hour_start else u'')

    @api.onchange('hour_start')
    def _onchange_hour_start(self):
        """ Sets end hour to start hour if no start hour """
        for activity in self:
            if activity.hour_start and not activity.hour_stop:
                activity.hour_stop = activity.hour_start + 1

    @api.constrains('hour_start', 'hour_stop')
    def _check_hour_period(self):
        """ Check if end hour if after start hour """
        for activity in self:
            if activity.hour_start > activity.hour_stop:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))


class ProductTemplate(models.Model):
    """ GOLEM Activity Product adaptations """
    _inherit = 'product.template'

    type = fields.Selection(default='service')
    default_code = fields.Char(copy=True)
    categ_id = fields.Many2one(copy=True)


class ProductCategory(models.Model):
    """ Product Category adaptations """
    _inherit = 'product.category'

    property_account_income_categ_id = fields.Many2one(required=True)
    property_account_expense_categ_id = fields.Many2one(required=True)

class ResPartner(models.Model):
    """ GOLEM Member partner adaptations """
    _inherit = 'res.partner'

    is_animator = fields.Boolean()
