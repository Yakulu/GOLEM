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

    activity_session_registration_ids = fields.One2many(
        'golem.activity.session.registration', 'member_id', 'Activities')


class GolemActivitySession(models.Model):
    _inherit = 'golem.activity.session'
    _sql_constraints = [('golem_activity_session_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    activity_session_registration_ids = fields.One2many(
        'golem.activity.session.registration', 'session_id', 'Members')
    places_used = fields.Integer('Places used', compute='_compute_places_used')

    @api.one
    @api.depends('activity_session_registration_ids')
    def _compute_places_used(self):
        self.places_used = len(self.activity_session_registration_ids)

    places = fields.Integer('Places', default=20)
    places_remain = fields.Integer('Remaining places', store=True,
                                   compute='_compute_places_remain')

    @api.one
    @api.depends('places', 'activity_session_registration_ids')
    def _compute_places_remain(self):
        used = len(self.activity_session_registration_ids)
        self.places_remain = self.places - used

    @api.constrains('places_remain')
    def _check_remaining_places(self):
        """ Forbid inscription when there is no more place """
        for s in self:
            if s.places_remain < 0:
                emsg = _('Sorry, there is no more place !')
                raise models.ValidationError(emsg)


class GolemActivitySessionRegistration(models.Model):
    _name = 'golem.activity.session.registration'
    _description = 'GOLEM Activity Session Registration'

    member_id = fields.Many2one('golem.member', string='Member', required=True,
                                ondelete='cascade')
    session_id = fields.Many2one('golem.activity.session', required=True,
                                 string='Activity session', ondelete='cascade')
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 ondelete='set null')
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice line',
                                      ondelete='set null')
    season_id = fields.Many2one(string='Season',
                                related='session_id.season_id')

    season_default_id = fields.Many2one('golem.season', 'Default season',
                                        compute='_compute_season_default')

    @api.one
    @api.depends('session_id')
    def _compute_season_default(self):
        """ Compute default season """
        domain = [('is_default', '=', True)]
        self.season_default_id = self.env['golem.season'].search(domain).id