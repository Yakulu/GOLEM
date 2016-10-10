# -*- coding: utf-8 -*-

#    copyright 2016 fabien bourgeois <fabien@yaltik.com>
#
#    this program is free software: you can redistribute it and/or modify
#    it under the terms of the gnu affero general public license as
#    published by the free software foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    this program is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.

from openerp import models, fields, api, _


class GolemMember(models.Model):
    _inherit = 'golem.member'

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'member_id', 'Activities')


class GolemActivity(models.Model):
    _inherit = 'golem.activity'
    _sql_constraints = [('golem_activity_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    activity_registration_ids = fields.One2many('golem.activity.registration',
                                                'activity_id', 'Members')
    places_used = fields.Integer('Places used', compute='_compute_places_used',
                                 store=True)

    @api.one
    @api.depends('activity_registration_ids')
    def _compute_places_used(self):
        self.places_used = len(self.activity_registration_ids)

    places = fields.Integer('Places', default=20)
    places_remain = fields.Integer('Remaining places', store=True,
                                   compute='_compute_places_remain')

    @api.one
    @api.depends('places', 'places_used')
    def _compute_places_remain(self):
        self.places_remain = self.places - self.places_used

    @api.constrains('places_remain')
    def _check_remaining_places(self):
        """ Forbid inscription when there is no more place """
        for s in self:
            if s.places_remain < 0:
                emsg = _('Sorry, there is no more place !')
                raise models.ValidationError(emsg)


class GolemActivityRegistration(models.Model):
    _name = 'golem.activity.registration'
    _description = 'GOLEM Activity Registration'

    member_id = fields.Many2one('golem.member', string='Member', required=True,
                                ondelete='cascade')
    activity_id = fields.Many2one('golem.activity', required=True,
                                  string='Activity', ondelete='cascade')
    season_id = fields.Many2one(string='Season',
                                related='activity_id.season_id')
    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current')

    _sql_constraints = [
        ('registration_uniq', 'UNIQUE (member_id, activity_id)',
         _('This member has already been registered for this activity.'))]

    @api.constrains('member_id', 'activity_id')
    def _check_season_reliability(self):
        """ Forbid registration when member season if not coherent with
        activity season or are duplicates """
        for r in self:
            if r.activity_id.season_id not in r.member_id.season_ids:
                emsg = _('Subscription can not be executed : the targeted '
                         'member is not on the same season as the activity.')
                raise models.ValidationError(emsg)
