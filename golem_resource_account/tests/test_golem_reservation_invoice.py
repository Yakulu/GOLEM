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

""" GOLEM Resource Reservation testing """

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
_LOGGER = logging.getLogger(__name__)


class TestGolemResourceReservation(TransactionCase):
    """ GOLEM Resource Reservation testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource Reservation """
        super(TestGolemResourceReservation, self).setUp(*args, **kwargs)
        self.resource = self.env['golem.resource'].create({
            'name': 'Resource',
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01',
            'availibility_24_7': True
        })

        self.partner = self.env['res.partner'].create({'firstname': 'John',
                                                       'lastname': 'DOE',
                                                       'is_company': False})
        self.partner2 = self.env['res.partner'].create({'firstname': 'John',
                                                        'lastname': 'DOE',
                                                        'is_company': False})
        self.data = {
            'resource_id': self.resource.id,
            'date_start': '2018-02-05 11:00:00', # is monday
            'date_stop': '2018-02-05 12:00:00',
            'partner_id': self.partner.id
        }
        self.data2 = {
            'resource_id': self.resource.id,
            'date_start': '2018-03-05 11:00:00', # is monday
            'date_stop': '2018-03-05 12:00:00',
            'partner_id': self.partner2.id
        }
        self.res_obj = self.env['golem.resource.reservation']


    def test_single_reservation_invoice(self):
        """ Test reservation bases """
        reservation = self.res_obj.create(self.data)
        self.assertEqual(reservation.state, 'draft')
        self.assertFalse(reservation.invoice_id)
        #try to create invoice withoud validating reservation
        with self.assertRaises(UserError) as err:
            reservation.create_invoice()
        self.assertIn(u'is not validated, please validate it', err.exception.args[0])
        reservation.state_confirm()

        #try to create invoice with no product linked
        with self.assertRaises(UserError) as err:
            reservation.create_invoice()
        self.assertIn(u'no product linked to resource', err.exception.args[0])

        reservation.resource_id.write({
            'product_tmpl_id': self.env.ref('product.product_product_5').id})
        reservation.create_invoice()
        self.assertTrue(reservation.invoice_id)
        self.assertEqual(reservation.invoicing_state, "draft")

    def test_multiple_reservation_in(self):
        """ Test Multiple Reservation Invoices """
        reservation_1 = self.res_obj.create(self.data)
        reservation_2 = self.res_obj.create(self.data2)
        #reservations = [reservation_1, reservation_2]
        reservation_1.state_confirm()
        reservation_2.state_confirm()
        self.assertEqual(reservation_1.state, "validated")
        self.assertEqual(reservation_2.state, "validated")
        reservation_1.resource_id.write({
            'product_tmpl_id': self.env.ref('product.product_product_5').id})
        reservation_2.resource_id.write({
            'product_tmpl_id': self.env.ref('product.product_product_5').id})
        wizard = self.env['golem.reservation.invoice.wizard'].create({
            'reservation_ids': [(4, reservation_1.id, 0), (4, reservation_2.id, 0)]})
        self.assertTrue(wizard.reservation_ids)
        self.assertEqual(wizard.reservation_ids[0], reservation_2)
        self.assertEqual(wizard.reservation_ids[1], reservation_1)
        #try to create invoice for to different client
        with self.assertRaises(UserError) as err:
            wizard.create_invoices()
        self.assertIn(u'group reservations of multiple clients in the same', err.exception.args[0])
        #fixing the same client for both reservation
        reservation_2.write({'partner_id': self.partner.id})
        wizard.create_invoices()
        self.assertTrue(reservation_1.invoice_id)
        self.assertTrue(reservation_2.invoice_id)
