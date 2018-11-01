# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

""" GOLEM Activity Registration Invoicing Wizard """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemActivityRegistrationInvoicing(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Wizard """
    _inherit = 'golem.activity.registration.invoicing'

    guardian_ids = fields.Many2many('res.partner', compute='_compute_guardian_ids')
    on_the_name_of = fields.Many2one('res.partner', 'On the Name of',
                                     ondelete='cascade')
    is_minor = fields.Boolean(related='member_id.is_minor')

    @api.depends('member_id')
    def _compute_guardian_ids(self):
        for rec in self:
            guardian_ids = rec.member_id.legal_guardian_ids.mapped('legal_guardian_id').ids
            rec.guardian_ids = [(6, 0, guardian_ids)]

    @api.multi
    def _create_invoice(self):
        """ Create invoice and lines """
        self.ensure_one()
        invoice = super(GolemActivityRegistrationInvoicing, self)._create_invoice()
        if self[0].is_minor:
            invoice.write({'partner_id': self[0].on_the_name_of.id,
                           'is_minor_invoice': True,
                           'partner_ids': [(6, 0, [self[0].on_the_name_of.id,
                                                   self[0].member_id.partner_id.id])]})
        return invoice

    def _create_payments(self, invoice):
        """ Create payment if schedule has been chosen : handling minor case """
        self.ensure_one()
        payments = super(GolemActivityRegistrationInvoicing, self)._create_payments(invoice)
        if self.on_the_name_of:
            payments.write({'partner_id': self.on_the_name_of.id})
        return payments

    @api.multi
    def validate(self):
        """ Validate and create invoice and payments """
        self.ensure_one()
        action = super(GolemActivityRegistrationInvoicing, self).validate()
        if self.is_minor and not self.on_the_name_of:
            err = _('This member is a minor, please fill on the name of so you '
                    'invoice this registration')
            raise ValidationError(err)
        return action

