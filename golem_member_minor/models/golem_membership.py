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


    src_member_id = fields.Many2one('golem.member')
    partner_id = fields.Many2one(required=True)

    @api.onchange('src_member_id')
    def onchange_member(self):
        """ Set partner domain if src_member_id is filled """
        record = self[0]
        if record.src_member_id.is_minor:
            return {'domain': {'partner_id':
                               [('id', 'in', record.src_member_id.legal_guardian_ids.ids)]
                              }
                   }
    @api.multi
    def membership_invoice(self):
        """ Add partners concerned to invoice and move membership from legal guardian to minor """
        self.ensure_one()
        record = self[0]
        res = super(GolemMembershipInvoice, self).membership_invoice()
        if record.src_member_id and record.src_member_id.is_minor:
            #gettin invoice_id from action's domain already declared
            invoice_id = (res['domain'][0][2] if
                          res['domain'][0][2] else False)
            if invoice_id:
                invoice = self.env['account.invoice'].browse(invoice_id)
                invoice.is_minor_invoice = True
                invoice.partner_ids = [(6, 0, [record.partner_id.id,
                                               record.src_member_id.partner_id.id])]
            # move the created membership from legal guardian to the minor
            membership_line = record.partner_id.member_lines[0]
            membership_line.copy({'partner': record.src_member_id.partner_id.id})
            membership_line.unlink()
        return res
