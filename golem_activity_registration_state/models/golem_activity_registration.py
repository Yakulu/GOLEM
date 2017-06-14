# -*- coding: utf-8 -*-

#    copyright 2017 fabien bourgeois <fabien@yaltik.com>
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

""" GOLEM Activity Registration State """

from odoo import models, fields, api, _

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    has_draft_registrations = fields.Boolean(
        'Has draft registrations ?',
        compute='_compute_has_draft_reg')

    @api.depends('activity_registration_ids')
    def _compute_has_draft_reg(self):
        """ Check if there are draft states in member activities """
        for member in self:
            for reg in member.activity_registration_ids:
                if reg.state == 'draft':
                    member.has_draft_registrations = True
                    return
            member.has_draft_registrations = False

    @api.multi
    def do_validate_registrations(self):
        """ Validate all draft registrations """
        self.ensure_one()
        member = self[0]
        draft_registrations = member.activity_registration_ids.filtered(
            lambda r: r.state == 'draft')
        if draft_registrations:
            invoicing = self.env['golem.activity.registration.invoicing'].create({
                'member_id' : member.id,
                'season_id': draft_registrations[0].activity_id.season_id.id
            })
            line_obj = self.env['golem.activity.registration.invoicing.line']
            for reg in draft_registrations:
                line_obj.create({'invoicing_id': invoicing.id,
                                 'activity_id': reg.activity_id.id,
                                 'price': reg.activity_id.list_price})
            return {'name': _('Registration invoicing'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'golem.activity.registration.invoicing',
                    'view_mode': 'form',
                    'res_id': invoicing.id,
                    'target': 'new'}

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
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 ondelete='set null')
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice line',
                                      ondelete='set null')

    @api.multi
    def write(self, values):
        """ Recomputes values linked to registrations when state change """
        res = super(GolemActivityRegistration, self).write(values)
        if values['state']:
            for registration in self:
                registration.activity_id.compute_places_used()
        return res
