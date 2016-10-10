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

from openerp import models, fields, api


class GolemMember(models.Model):
    _inherit = 'golem.member'

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
            for rem in r_removed:
                r = rObj.browse([rem[1]])
                # if already canceled, let it be removed, else cancel it
                if r.state != 'canceled':
                    r.state = 'canceled'
                else:
                    r_keep.append(rem)
            values['activity_session_registration_ids'] = r_keep
        return super(GolemMember, self).write(values)


class GolemActivitySession(models.Model):
    _inherit = 'golem.activity.session'

    @api.one
    @api.depends('activity_session_registration_ids')
    def _compute_places_used(self):
        rids = self.activity_session_registration_ids
        self.places_used = len(rids.filtered(lambda r: r.state == 'confirmed'))


class GolemActivitySessionRegistration(models.Model):
    _inherit = 'golem.activity.session.registration'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                              ('canceled', 'Canceled')], required=True,
                             default='draft')
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 ondelete='set null')
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice line',
                                      ondelete='set null')

    @api.multi
    def write(self, values):
        """ Recomputes values linked to registrations when state change """
        res = super(GolemActivitySessionRegistration, self).write(values)
        if values['state']:
            for r in self:
                r.session_id._compute_places_used()
        return res
