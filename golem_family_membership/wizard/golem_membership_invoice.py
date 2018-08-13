# -*- coding: utf-8 -*-

#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

""" GOLEM Membership Invoice Adaptations"""

from odoo import models, fields, api

class GolemMembershipInvoice(models.TransientModel):
    """ GOLEM Membership Invoice adaptations """
    _inherit = 'golem.membership.invoice'

    family_id = fields.Many2one('golem.family')
    members_ids = fields.Many2many('res.partner')
    on_the_name_of = fields.Many2one('res.partner', domain="[('id', '=', members_ids[0][2])]")

    @api.onchange('family_id')
    def onchange_family_id(self):
        """ fill members_ids """
        for record in self:
            for member in record.family_id.member_ids:
                record.members_ids += member

    @api.multi
    def membership_family_invoice(self):
        """ Create family membership """
        self.ensure_one()
        record = self[0]
        datas = {'membership_product_id': self.product_id.id,
                 'amount': self.member_price}
        invoice_list = record.on_the_name_of.create_membership_invoice(datas=datas)
        datas = {'membership_product_id': self.product_id.id,
                 'amount': 0}
        gen = (member for member in record.members_ids if member != record.on_the_name_of)
        for member in gen:
            id_membership = member.create_membership_invoice(datas=datas)
            self.env['account.invoice'].browse(id_membership).action_invoice_open()
            invoice_list += id_membership

        search_view_id = self.env.ref('account.view_account_invoice_filter')
        form_view_id = self.env.ref('account.invoice_form')
        return {
            'domain': [('id', 'in', invoice_list)],
            'name': 'Membership Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (form_view_id.id, 'form')],
            'search_view_id': search_view_id.id
        }
