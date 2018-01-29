# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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

from odoo import models, fields, api, _

class GolemActivityType(models.Model):
    """ GOLEM Activity Type """
    _name = 'golem.activity.type'
    _description = 'GOLEM Activity Type'

    _sql_constraints = [('golem_activity_type_name_uniq', 'UNIQUE (name)',
                         _('This activity type name has already been used.'))]

    name = fields.Char('Activity type', required=True, translate=True)
    is_recurrent = fields.Boolean('Is recurrent?')

class GolemActivity(models.Model):
    """ GOLEM Activity """
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

    @api.multi
    @api.depends('name', 'default_code')
    def _compute_full_name(self):
        """ Provide a better displayed name """
        for activity in self:
            full_name = unicode(activity.name)
            if activity.default_code:
                full_name = u'[{}] {}'.format(activity.default_code, full_name)
            activity.full_name = full_name

    @api.model
    def _default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain)

    season_id = fields.Many2one('golem.season', string='Season', copy=False,
                                required=True, default=_default_season,
                                ondelete='restrict')

    is_current = fields.Boolean('Current season?', store=True, default=False,
                                compute='compute_is_current')

    @api.depends('season_id')
    def compute_is_current(self):
        """ Checks if activity is active for current season """
        default_season = self._default_season()
        for activity in self:
            activity.is_current = (default_season == activity.season_id)

    animator_id = fields.Many2one('res.partner', string='Animator',
                                  domain=[('is_company', '=', False)])
    categ_id = fields.Many2one('product.category',
                               help='Select category for the current activity')
    type_id = fields.Many2one('golem.activity.type', required=True, index=True,
                              string='Type')
    is_recurrent = fields.Boolean(related='type_id.is_recurrent')
    date_start = fields.Date('Start date', copy=False)
    date_stop = fields.Date('End date', copy=False)

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
            if activity.date_start and activity.date_stop and \
                    activity.date_start > activity.date_stop:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))
            if activity.season_id.date_start > activity.date_start < activity.season_id.date_end:
                msg = _(u'Start of the activity is not in range of an '
                        'existing period.')
                raise models.ValidationError(msg)
            if activity.season_id.date_end < activity.date_stop > activity.season_id.date_start:
                msg = _(u'End of the activity is not in range of an '
                        'existing period.')
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
