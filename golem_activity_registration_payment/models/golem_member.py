# -*- coding: utf-8 -*-

#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Member adaptations """

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    has_invoicable_registrations = fields.Boolean(
        'Has invoicable registrations ?',
        compute='_compute_has_invoicable_reg')

    @api.depends('activity_registration_ids', 'activity_registration_ids.state')
    def _compute_has_invoicable_reg(self):
        """ Check if there are confirmed registrations with no invoice linked """
        for member in self:
            regis = member.activity_registration_ids
            regis = regis.filtered(lambda r: r.state == 'confirmed' and not r.invoice_line_id)
            member.has_invoicable_registrations = bool(len(regis))

    @api.multi
    def invoice_registrations(self):
        """ Launch wizard to generate invoices for registrations """
        self.ensure_one()
        member = self[0]
        registrations = member.activity_registration_ids.filtered(
            lambda r: r.state == 'confirmed' and not r.invoice_line_id
        )
        if registrations:
            invoicing = self.env['golem.activity.registration.invoicing'].create({
                'member_id' : member.id,
                'season_id': registrations[0].activity_id.season_id.id
            })
            line_obj = self.env['golem.activity.registration.invoicing.line']
            for reg in registrations:
                line_obj.create({'invoicing_id': invoicing.id,
                                 'registration_id': reg.id,
                                 'activity_id': reg.activity_id.id,
                                 'price': reg.activity_id.list_price})
            return {'name': _('Registration invoicing'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'golem.activity.registration.invoicing',
                    'view_mode': 'form',
                    'res_id': invoicing.id,
                    'target': 'new'}
        else:
            uerr = _('All confirmed registrations had already been invoiced.')
            raise UserError(uerr)
