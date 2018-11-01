# -*- coding: utf-8 -*-
#
#    Copyright 2018 Michel Dessenne <michel@yaltik.com>
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

from odoo import models, fields, api


class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    total_paid = fields.Monetary(compute='_compute_total_paid', store=True,
                                 groups='account.group_account_invoice')
    last_payment_state = fields.Selection([('draft', 'Draft'),
                                           ('posted', 'Posted'),
                                           ('checked', 'Checked'),
                                           ('reconciled', 'Reconciled')],
                                          compute='_compute_last_payment_state')

    @api.depends('invoice_ids.payment_ids', 'invoice_ids.payment_ids.state',
                 'invoice_ids.payment_ids.amount')
    def _compute_total_paid(self):
        """ Computes total paid """
        for member in self:
            payments = member.invoice_ids.mapped('payment_ids')
            member.total_paid = sum(
                payments.filtered(lambda p: p.state != 'draft').mapped('amount')
            )

    @api.multi
    def open_partner_invoices(self):
        """ Open member invoices """
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['context'] = {'type':'out_invoice', 'journal_type': 'sale',
                             'search_default_partner_id': self[0].partner_id.id,
                             'default_partner_id': self[0].partner_id.id}
        return action

    @api.multi
    def open_partner_payments(self):
        """ Open member payments """
        self.ensure_one()
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {'default_payment_type': 'inbound',
                             'default_partner_type': 'customer',
                             'search_default_partner_id': self[0].partner_id.id,
                             'default_partner_id': self[0].partner_id.id}
        return action

    @api.depends('invoice_ids')
    def _compute_last_payment_state(self):
        """ Computes last invoice payment state : check last invoice, then more
        recent payment and retrieve its state """
        for member in self:
            if member.invoice_ids:
                invoice_ids = member.invoice_ids.filtered(lambda inv: inv.state in ('open', 'paid'))
                invoice_ids = invoice_ids.sorted(key=lambda r: r.date_invoice, reverse=True)
                payment_ids = invoice_ids[0].payment_ids if invoice_ids else False
                if payment_ids:
                    payment_ids = payment_ids.sorted(lambda r: r.payment_date, reverse=True)
                    today = fields.Date.today()
                    last_payment_id = None
                    for payment in payment_ids:
                        if payment.payment_date < today:
                            last_payment_id = payment
                            break
                    if last_payment_id:
                        member.last_payment_state = last_payment_id.state
                        return
            member.state_last_invoice = False
