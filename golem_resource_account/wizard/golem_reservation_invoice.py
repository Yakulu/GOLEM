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

""" GOLEM Reservation Invoice Wizard"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class GolemReservationInvoiceWizard(models.TransientModel):
    """ GOLEM Resource Reservation Invoice Wizard """
    _name = 'golem.reservation.invoice.wizard'

    reservation_ids = fields.Many2many('golem.resource.reservation',
                                       default=lambda self: self._context.get('active_ids', []),
                                       string='Reservations to invoice')

    @api.multi
    def create_invoices(self):
        """ Create invoices for reservation """
        self.ensure_one()
        if self.reservation_ids:

            inv_obj = self.env['account.invoice']
            partner_id = self.reservation_ids[0].partner_id
            product = self.reservation_ids[0].resource_id.product_tmpl_id

            if product.id:
                account_id = product.property_account_income_id.id
            if not account_id:
                account_id = product.categ_id.property_account_income_categ_id.id
            if not account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". \
                       You may have to install a chart of account from Accounting \
                       app, settings menu.') % (product.name,))

            lines = []

            for reservation in self.reservation_ids:
                if reservation.state != "validated":
                    raise UserError(
                        _("The reservation '%s' is not validated, please validate it before \
                          creating invoice") % reservation.name)
                product = reservation.resource_id.product_tmpl_id
                if not product:
                    raise UserError(
                        _("There is no product linked to resource : '%s', you can't invoice \
                          reservation with no product linked") % (reservation.resource_id.name,))
                if partner_id != reservation.partner_id:
                    raise UserError(
                        _("You can't group reservations of multiple clients in the same \
                           invoice, please remove inadequate reservations"))

                amount = product.standard_price
                delta = fields.Datetime.from_string(reservation.date_stop) - \
                fields.Datetime.from_string(reservation.date_start)

                quantity = (delta.days * 24) + (delta.seconds/3600.0)
                lines.append((0, 0, {
                    'name': reservation.resource_id.name,
                    #'origin': ,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': quantity,
                    'discount': 0.0,
                    'uom_id': product.uom_id.id,
                    'product_id': product.id,
                    }))
            invoice = inv_obj.create({
                #'name': reservation.name,
                #'origin': ,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id,
                'invoice_line_ids': lines,
                })
            self.reservation_ids.write({'invoice_id': invoice.id})
            if self._context.get('open_invoices', False):
                return {'name' : _('Reservation Invoice'),
                        'type' : 'ir.actions.act_window',
                        'res_model' : 'account.invoice',
                        'res_id' : invoice.id,
                        'view_mode': 'form',
                        'view_id': self.env.ref('account.invoice_form').id,
                        'target': 'current'}
            return {'type': 'ir.actions.act_window_close'}
