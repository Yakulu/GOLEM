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

""" GOLEM Activity Registration Invoicing Wizard """

import logging
from odoo import models, fields, api
_LOGGER = logging.getLogger(__name__)

class GolemActivityRegistrationInvoicingLine(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Lines """
    _name = 'golem.activity.registration.invoicing.line'
    description = 'GOLEM Activity Registration Invoicing Lines'

    invoicing_id = fields.Many2one('golem.activity.registration.invoicing',
                                   required=True)
    registration_id = fields.Many2one('golem.activity.registration', required=True)
    activity_id = fields.Many2one('golem.activity', required=True, readonly=True)
    price = fields.Float('Price')

class GolemActivityRegistrationInvoicing(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Wizard """
    _name = 'golem.activity.registration.invoicing'
    _description = 'GOLEM Activity Registration Invoicing Wizard'

    season_id = fields.Many2one('golem.season', 'Season', required=True)
    member_id = fields.Many2one('golem.member', 'Member', required=True)
    line_ids = fields.One2many('golem.activity.registration.invoicing.line',
                               'invoicing_id', string='Activities')
    schedule_id = fields.Many2one('golem.payment.schedule', 'Payment schedule',
                                  domain='[("season_id", "=", season_id)]',
                                  help='If no schedule is selected, only the '
                                  'invoice will be create. Otherwise, draft '
                                  'payments will be generated.')
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))])

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
        if self.schedule_id and self.schedule_id.occurences > 0:
            # TODO: make more intelligent price cut
            amount = invoice.amount_total
            amount_per_occurence = amount / self.schedule_id.occurences
            for day in self.schedule_id.day_ids:
                payment = self.env['account.payment'].new({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': self.member_id.partner_id.id,
                    'amount': amount_per_occurence,
                    'payment_date': day.day,
                    'journal_id': self.journal_id.id,
                })
                payment._onchange_journal()
                payment_values = dict(payment._cache)
                payment = self.env['account.payment'].create(payment_values)
                payment.invoice_ids = [(4, invoice.id, False)]

    @api.multi
    def validate(self):
        """ Validate and create invoice and payments """
        self.ensure_one()
        draft_registrations = self.member_id.activity_registration_ids.filtered(
            lambda r: r.state == 'draft')
        draft_registrations.write({'state': 'confirmed'})
        invoice = self._create_invoice()
        self._create_payments(invoice)
