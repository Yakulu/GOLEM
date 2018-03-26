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
from odoo.exceptions import UserError


class GolemReservationInvoiceWizard(models.TransientModel):
    """ GOLEM Resource Reservation Invoice Wizard """
    _name = 'golem.reservation.invoice.wizard'

    reservation_ids = fields.Many2many(
        'golem.resource.reservation', required=True, string='Reservations to invoice',
        default=lambda self: self._context.get('active_ids', []))

    @api.multi
    def create_invoice(self):
        """ Invoice creation """
        self.ensure_one()

        self.reservation_ids.check_before_invoicing()
        self.reservation_ids[0].create_invoice()
        if len(self.reservation_ids) > 1:
            invoice_id = self.reservation_ids[0].invoice_id
            self.reservation_ids[1:].create_invoice_line(invoice_id)

        # return {}
