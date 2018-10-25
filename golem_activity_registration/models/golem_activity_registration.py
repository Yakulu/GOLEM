# -*- coding: utf-8 -*-
#
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

""" GOLEM Activity Registration """

from odoo import models, fields, api, _

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'member_id',
                                                'Activities for default season',
                                                domain=[('is_default', '=', True)])
    activity_registration_all_ids = fields.One2many('golem.activity.registration',
                                                    'member_id', 'All activities')


class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'
    _sql_constraints = [('golem_activity_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'activity_id', 'Members',
                                                index=True)
    places_used = fields.Integer('Places used', compute='compute_places_used',
                                 store=True)
    only_for_subscriber = fields.Boolean(default=False)

    @api.multi
    @api.depends('activity_registration_ids')
    def compute_places_used(self):
        """ Computes used places """
        for activity in self:
            activity.places_used = len(activity.activity_registration_ids)

    places = fields.Integer('Places', default=20)
    places_remain = fields.Integer('Remaining places', store=True,
                                   compute='_compute_places_remain')

    @api.multi
    @api.depends('places', 'places_used')
    def _compute_places_remain(self):
        """ Computes remaining places """
        for activity in self:
            activity.places_remain = activity.places - activity.places_used

    @api.constrains('places_remain')
    def _check_remaining_places(self):
        """ Forbid inscription when there is no more place """
        for activity in self:
            if activity.places_remain < 0:
                emsg = _('Sorry, there is no more place !')
                raise models.ValidationError(emsg)


class GolemActivityRegistration(models.Model):
    """ GOLEM Activity Registration """
    _name = 'golem.activity.registration'
    _description = 'GOLEM Activity Registration'
    _rec_name = 'activity_id'

    member_id = fields.Many2one('golem.member', string='Service user',
                                required=True, ondelete='cascade', index=True)
    activity_id = fields.Many2one('golem.activity', required=True, index=True,
                                  string='Activity', ondelete='cascade')
    activity_price = fields.Float(related='activity_id.list_price')
    season_id = fields.Many2one(string='Season',
                                related='activity_id.season_id', store=True)
    is_default = fields.Boolean('Default season?',
                                related='activity_id.is_default')

    _sql_constraints = [
        ('registration_uniq', 'UNIQUE (member_id, activity_id)',
         _('This member has already been registered for this activity.'))]

    @api.onchange('activity_id', 'activity_id.only_for_subscriber')
    def onchange_activity_subcrib(self):
        """ If activity only for subscribers : do not allow non subscribers """
        domain = []
        if self.activity_id.only_for_subscriber:
            domain.append(('membership_state', 'not in', ('none', 'canceled', 'old')))
        return {'domain':  {'member_id': domain}}

    @api.onchange('member_id')
    def onchange_member_subcrib(self):
        """ If not subscriber : do not show subscribers only activities """
        domain = []
        if self.member_id and self.member_id.membership_state in ('none', 'canceled', 'old'):
            domain.append(('only_for_subscriber', '=', False))
        return {'domain':  {'activity_id': domain}}


    @api.constrains('member_id', 'activity_id')
    def _check_season_reliability(self):
        """ Forbid registration when member season if not coherent with
        activity season or are duplicates """
        for reg in self:
            if (reg.activity_id.only_for_subscriber and \
                reg.member_id.membership_state in ['none', 'canceled', 'old']):
                emsg = _('Subscription can not be executed : the targeted '
                         'activity is only for subscriber.')
                raise models.ValidationError(emsg)
            if reg.activity_id.season_id not in reg.member_id.season_ids:
                emsg = _('Subscription can not be executed : the targeted '
                         'member is not on the same season as the activity.')
                raise models.ValidationError(emsg)
