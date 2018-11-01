# -*- coding: utf-8 -*-

#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Membership """

from odoo import models, fields, api


class GolemMembershipInvoice(models.TransientModel):
    """ Membership invoicing """
    _inherit = 'golem.membership.invoice'


    src_member_id = fields.Many2one('golem.member', ondelete='cascade')
    src_member_minor = fields.Boolean(related='src_member_id.is_minor')

    @api.onchange('src_member_id')
    def onchange_member(self):
        """ Set partner domain if src_member_id is filled """
        self.ensure_one()
        record  = self[0]
        domain = ([('id', 'in',
                    record.src_member_id.mapped('legal_guardian_ids.legal_guardian_id').ids)]
                  if record.src_member_id.is_minor else [])
        return {'domain': {'partner_id': domain}}

    @api.multi
    def membership_invoice(self):
        """ Add partners concerned to invoice and move membership from legal
        guardian to minor """
        self.ensure_one()
        record = self[0]
        res = super(GolemMembershipInvoice, self).membership_invoice()
        if record.src_member_id.is_minor:
            # Getting invoice IDS from action's domain already declared
            invoice_ids = (res['domain'][0][2] or False)
            if invoice_ids: # As invoice_ids is a Python list, empty or not
                invoice = self.env['account.invoice'].browse(invoice_ids)[-1]
                invoice.is_minor_invoice = True
                invoice.partner_ids = [(6, 0, [record.partner_id.id,
                                               record.src_member_id.partner_id.id])]
            # move the created membership from legal guardian to the minor
            membership_line = record.partner_id.member_lines[0]
            membership_line.copy({'partner': record.src_member_id.partner_id.id})
            membership_line.unlink()
        return res
