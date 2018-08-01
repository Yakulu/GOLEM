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

""" GOLEM Activity Registration Invoicing Wizard """

import logging
from math import ceil
from odoo import models, fields, api, _
from odoo.exceptions import UserError
_LOGGER = logging.getLogger(__name__)

class GolemActivityRegistrationInvoicingLine(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Lines """
    _name = 'golem.activity.registration.invoicing.line'
    _description = 'GOLEM Activity Registration Invoicing Lines'

    invoicing_id = fields.Many2one('golem.activity.registration.invoicing',
                                   required=True)
    registration_id = fields.Many2one('golem.activity.registration', required=True)
    activity_id = fields.Many2one('golem.activity', required=True, readonly=True)
    price = fields.Float()


class GolemActivityRegistrationInvoicing(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Wizard """
    _name = 'golem.activity.registration.invoicing'
    _description = 'GOLEM Activity Registration Invoicing Wizard'

    state = fields.Selection([('init', 'init'), ('final', 'final')],
                             default='init', required=True)
    season_id = fields.Many2one('golem.season', 'Season', required=True,
                                ondelete='cascade')
    member_id = fields.Many2one('golem.member', 'Member', required=True,
                                ondelete='cascade')
    line_ids = fields.One2many('golem.activity.registration.invoicing.line',
                               'invoicing_id', string='Activities')
    schedule_id = fields.Many2one('golem.payment.schedule', 'Payment schedule',
                                  domain='[("season_id", "=", season_id)]',
                                  ondelete='cascade',
                                  help='If no schedule is selected, only the '
                                  'invoice will be create. Otherwise, draft '
                                  'payments will be generated.')
    journal_id = fields.Many2one('account.journal', string='Payment method',
                                 domain=[('type', 'in', ('bank', 'cash'))],
                                 ondelete='cascade')
    invoice_id = fields.Many2one('account.invoice', string='Generated invoice',
                                 ondelete='cascade')
    payment_ids = fields.Many2many('account.payment', string='Generated payments')

    @api.multi
    def _create_invoice(self):
        """ Create invoice and lines """
        self.ensure_one()
        partner = self.member_id.partner_id
        invoice = self.env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': partner.property_account_receivable_id.id,
            'fiscal_position_id': partner.property_account_position_id.id
        })
        for line in self.line_ids:
            product = line.activity_id.product_id
            # Handling of invoice lines : needs cache record for onchange, then
            # real writing...
            invoice_line = self.env['account.invoice.line'].new({
                'product_id': product.id,
                'invoice_id': invoice.id
            })
            invoice_line._onchange_product_id()
            line_values = dict(invoice_line._cache)
            line_values['price_unit'] = line.price
            invoice_line = self.env['account.invoice.line'].create(line_values)
            invoice.compute_taxes()
            line.registration_id.invoice_line_id = invoice_line.id
        return invoice

    @api.multi
    def _create_payments(self, invoice):
        """ Create payment if schedule has been chosen """
        self.ensure_one()
        payments = self.env['account.payment']
        if self.schedule_id and self.schedule_id.occurences > 0:
            amount = invoice.amount_total
            amount_per_occurence = ceil(amount / self.schedule_id.occurences)
            for index, day in enumerate(self.schedule_id.day_ids):
                payment_amount = (amount_per_occurence if index !=
                                  (len(self.schedule_id.day_ids.ids) - 1)
                                  else amount)
                payment = self.env['account.payment'].new({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': self.member_id.partner_id.id,
                    'amount': payment_amount,
                    'payment_date': day.day,
                    'journal_id': self.journal_id.id,
                })
                amount -= amount_per_occurence
                payment._onchange_journal()
                payment_values = dict(payment._cache)
                payment = self.env['account.payment'].create(payment_values)
                payment.invoice_ids = [(4, invoice.id, False)]
                payments |= payment
        return payments

    @api.multi
    def validate(self):
        """ Validate and create invoice and payments """
        self.ensure_one()
        draft_registrations = self.member_id.activity_registration_ids.filtered(
            lambda r: r.state == 'draft')
        draft_registrations.write({'state': 'confirmed'})
        invoice = self._create_invoice()
        self.invoice_id = invoice
        payments = self._create_payments(invoice)
        self.payment_ids |= payments
        self.write({'state': 'final'})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self[0].id,
            'target': 'new'
        }

    @api.multi
    def go_invoice(self):
        """ Navigate to generated invoice """
        self.ensure_one()
        if not self.invoice_id:
            uerr = _('There is no generated invoice.')
            raise UserError(uerr)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated invoice'),
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': self[0].invoice_id.id
        }

    @api.multi
    def go_payments(self):
        """ Navigate to generated payments """
        self.ensure_one()
        if not self.payment_ids:
            uerr = _('There is no generated payments.')
            raise UserError(uerr)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated payments'),
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('id', 'in', self.payment_ids.ids)]
        }
