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
            'avaibility_stop': '2020-01-01'
        })
        self.resource_val = self.env['golem.resource'].create({
            'name': 'Resource to validate',
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01',
            'validation_required': True
        })

        self.timetable_obj = self.env['golem.resource.timetable']

        timetable_data = {'resource_id': self.resource.id, 'weekday': '0',
                          'time_start': 8.0, 'time_stop': 12.0}
        timetable_data2 = {'resource_id': self.resource.id, 'weekday': '1',
                           'availibility_24': True}
        timetable_data3 = {'resource_id': self.resource.id, 'weekday': '2',
                           'time_start': 7.0, 'time_stop': 23.98}
        timetable_data4 = {'resource_id': self.resource.id, 'weekday': '3',
                           'availibility_24': True}

        self.timetable_obj.create(timetable_data)
        self.timetable_obj.create(timetable_data2)
        self.timetable_obj.create(timetable_data3)
        self.timetable_obj.create(timetable_data4)

        timetable_data['resource_id'] = self.resource_val.id
        self.timetable_obj.create(timetable_data)

        self.partner = self.env['res.partner'].create({'firstname': 'John',
                                                       'lastname': 'DOE',
                                                       'is_company': False})

        self.data = {
            'resource_id': self.resource.id,
            'date_start': '2018-02-05 11:00:00', # is monday
            'date_stop': '2018-02-05 12:00:00',
            'partner_id': self.partner.id
        }
        self.res_obj = self.env['golem.resource.reservation']


    def test_reservation_invoice_single(self):
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
        self.assertEqual(reservation.invoicing_state,"draft")

        """
            self.assertEqual(reservation.state, 'validated')
            reservation.create_invoice()
            self.assertTrue(reservation.invoice_id)"""
