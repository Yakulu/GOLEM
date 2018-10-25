# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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
from odoo.addons import decimal_precision as dp


class GolemMembershipInvoice(models.TransientModel):
    """ Membership invoicing """
    _name = 'golem.membership.invoice'
    _description = 'GOLEM MemberShip invoicing'

    partner_id = fields.Many2one('res.partner', 'Partner', required=True,
                                 ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Membership',
                                 required=True)
    member_price = fields.Float('Member Price',
                                dp.get_precision('Product Price'),
                                required=True)

    @api.onchange('product_id')
    def onchange_product(self):
        """ Sets price according to product """
        for minvoice in self:
            if not minvoice.product_id:
                minvoice.member_price = False
            else:
                price = minvoice.product_id.price_get()[minvoice.product_id.id]
                minvoice.member_price = price

    @api.multi
    def membership_invoice(self):
        """ Create invoice and redirect to partner invoice list """
        self.ensure_one()
        datas = {'membership_product_id': self.product_id.id,
                 'amount': self.member_price}
        invoice_list = self.partner_id.create_membership_invoice(datas=datas)
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
