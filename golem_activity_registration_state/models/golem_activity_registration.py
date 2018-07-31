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

""" GOLEM Activity Registration State """

from odoo import models, fields, api

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    has_draft_registrations = fields.Boolean(
        'Has draft registrations ?',
        compute='_compute_has_draft_reg')

    @api.depends('activity_registration_ids', 'activity_registration_ids.state')
    def _compute_has_draft_reg(self):
        """ Check if there are draft states in member activities """
        for member in self:
            regis = member.activity_registration_ids
            regis = regis.filtered(lambda r: r.state == 'draft')
            member.has_draft_registrations = bool(len(regis))

    @api.multi
    def do_validate_registrations(self):
        """ Validate all draft registrations """
        self.ensure_one()
        member = self[0]
        member.activity_registration_ids.filtered(
            lambda r: r.state == 'draft'
        ).write({'state': 'confirmed'})

    @api.multi
    def write(self, values):
        """ Handle removed activities to be canceled """
        if 'activity_registration_ids' in values:
            rids = values['activity_registration_ids']
            r_keep, r_removed = [], []
            for rid in rids:  # == 2 is removal case
                if rid[0] == 2:
                    r_removed.append(rid)
                else:
                    r_keep.append(rid)
            reg_obj = self.env['golem.activity.registration']
            for rem in r_removed:
                reg = reg_obj.browse([rem[1]])
                # if already canceled, let it be removed, else cancel it
                if reg.state != 'canceled':
                    reg.state = 'canceled'
                else:
                    r_keep.append(rem)
            values['activity_registration_ids'] = r_keep
        return super(GolemMember, self).write(values)


class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'

    @api.multi
    @api.depends('activity_registration_ids')
    def compute_places_used(self):
        """ Computes used places """
        for activity in self:
            rids = activity.activity_registration_ids
            activity.places_used = len(rids.filtered(lambda r: r.state == 'confirmed'))


class GolemActivityRegistration(models.Model):
    """ GOLEM Activity Registration adaptations """
    _inherit = 'golem.activity.registration'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                              ('canceled', 'Canceled')], required=True,
                             default='draft')

    @api.multi
    def write(self, values):
        """ Recomputes values linked to registrations when state change """
        res = super(GolemActivityRegistration, self).write(values)
        if values.get('state'):
            for registration in self:
                registration.activity_id.compute_places_used()
        return res
