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
    has_draft_registrations = fields.Boolean(
        'Has draft registrations ?',
        compute='_compute_has_draft_registrations')

    @api.one
    @api.depends('activity_session_registration_ids')
    def _compute_has_draft_registrations(self):
        """ Check if there are draft states in member activities """
        for r in self.activity_session_registration_ids:
            if r.state == 'draft':
                self.has_draft_registrations = True
                return
        self.has_draft_registrations = False

    @api.one
    def do_validate_registrations(self):
        """ Validate all draft registrations """
        draft_registrations = self.activity_session_registration_ids.filtered(
            lambda r: r.state == 'draft')
        draft_registrations.write({'state': 'confirmed'})

    @api.multi
    def write(self, values):
        """ Handle removed activities to be canceled """
        if 'activity_session_registration_ids' in values:
            rids = values['activity_session_registration_ids']
            r_keep, r_removed = [], []
            for r in rids:  # == 2 is removal case
                r_removed.append(r) if r[0] == 2 else r_keep.append(r)
            rObj = self.env['golem.activity.session.registration']
            for r in r_removed:
                r = rObj.browse([r[1]])
                # if already canceled, let it be removed, else cancel it
                if r.state != 'canceled':
                    r.state = 'canceled'
                else:
                    r_keep.append(r)
            values['activity_session_registration_ids'] = r_keep
        return super(GolemMember, self).write(values)


class GolemActivitySession(models.Model):
    _inherit = 'golem.activity.session'
    _sql_constraints = [('golem_activity_session_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    activity_session_registration_ids = fields.One2many(
        'golem.activity.session.registration', 'session_id', 'Members')
    places_used = fields.Integer('Places used', compute='_compute_places_used',
                                 store=True)

    @api.one
    @api.depends('activity_session_registration_ids')
    def _compute_places_used(self):
        rids = self.activity_session_registration_ids
        self.places_used = len(rids.filtered(lambda r: r.state == 'confirmed'))

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


class GolemActivitySessionRegistration(models.Model):
    _name = 'golem.activity.session.registration'
    _description = 'GOLEM Activity Session Registration'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                              ('canceled', 'Canceled')], required=True,
                             default='draft')
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
    is_current = fields.Boolean('Current season?',
                                related='session_id.is_current')

    _sql_constraints = [
        ('registration_uniq', 'UNIQUE (member_id, session_id)',
         _('This member has already been registered for this session.'))]

    @api.constrains('member_id', 'session_id')
    def _check_season_reliability(self):
        """ Forbid registration when member season if not coherent with
        session season or are duplicates """
        for r in self:
            if r.session_id.season_id not in r.member_id.season_ids:
                emsg = _('Subscription can not be executed : the targeted '
                         'member is not on the same season as the session.')
                raise models.ValidationError(emsg)

    @api.multi
    def write(self, values):
        """ Recomputes values linked to registrations when state change """
        res = super(GolemActivitySessionRegistration, self).write(values)
        if values['state']:
            for r in self:
                r.session_id._compute_places_used()
        return res
