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

""" GOLEM Resource Reservation  Adaptation"""

from math import modf
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class GolemResourceReservation(models.Model):
    """ GOLEM Resource Reservation Adaptation """
    _inherit = 'golem.resource.reservation'

    invoice_id = fields.Many2one('account.invoice')
    invoice_state = fields.Selection(related="invoice_id.state")


    @api.multi
    def create_invoice(self):
        for reservation in self:
            inv_obj = self.env['account.invoice']
            partner_id = reservation.partner_id
            product = reservation.resource_id.product_tmpl_id
            amount = product.standard_price

            if product.id:
                account_id = product.property_account_income_id.id

            if not account_id:
                account_id = product.categ_id.property_account_income_categ_id.id

            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))


            invoice = inv_obj.create({
                'name': reservation.name,
                #'origin': self.application_number,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': reservation.resource_id.name,
                    #'origin': ,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': 1.0,
                    'discount': 0.0,
                    'uom_id': product.uom_id.id,
                    'product_id': product.id,
                    })],
                })
