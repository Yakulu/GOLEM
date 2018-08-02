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
from odoo.exceptions import ValidationError
_LOGGER = logging.getLogger(__name__)


class TestGolemResourceReservation(TransactionCase):
    """ GOLEM Resource Reservation testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource Reservation """
        super(TestGolemResourceReservation, self).setUp(*args, **kwargs)
        self.resource = self.env['golem.resource'].create({
            'name': 'Resource',
            'availability_start': '2018-01-01',
            'availability_stop': '2020-01-01'
        })
        self.resource_val = self.env['golem.resource'].create({
            'name': 'Resource to validate',
            'availability_start': '2018-01-01',
            'availability_stop': '2020-01-01',
            'validation_required': True
        })

        self.timetable_obj = self.env['golem.resource.timetable']

        timetable_data = {'resource_id': self.resource.id, 'weekday': '0',
                          'time_start': 8.0, 'time_stop': 12.0}
        timetable_data2 = {'resource_id': self.resource.id, 'weekday': '1',
                           'availability_24': True}
        timetable_data3 = {'resource_id': self.resource.id, 'weekday': '2',
                           'time_start': 7.0, 'time_stop': 23.98}
        timetable_data4 = {'resource_id': self.resource.id, 'weekday': '3',
                           'availability_24': True}

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

    def test_reservation_basic(self):
        """ Test reservation bases """
        reservation = self.res_obj.create(self.data)
        self.assertEqual(reservation.partner_id, self.partner)
        self.assertEqual(reservation.user_id, self.env.user)
        self.assertEqual(reservation.date_start, '2018-02-05 11:00:00')
        self.assertEqual(reservation.date_stop, '2018-02-05 12:00:00')
        self.assertEqual(reservation.state, 'draft')
        self.assertFalse(reservation.rejection_reason)
        self.assertEqual(reservation.name, 'Resource/2018-02-05 11:00:00')
        self.assertEqual(reservation.resource_id, self.resource)
        self.assertEqual(len(reservation.resource_timetable_ids), 4)
        self.assertEqual(reservation.resource_id.reservation_ids[0], reservation)

    def test_reservation_hours(self):
        """ Test thats stop date can not be after or equal start date """
        self.data['date_stop'] = '2018-02-05 10:00:00'
        with self.assertRaises(ValidationError):
            self.res_obj.create(self.data)
        with self.assertRaises(ValidationError):
            self.res_obj.create({
                'resource_id': self.resource.id,
                'date_start': '2018-02-05 11:00:00',
                'date_stop': '2018-02-05 11:00:00',
                'partner_id': self.partner.id})

    def test_state_basic(self):
        """ Tests basic state methods """
        reservation = self.res_obj.create(self.data)
        self.assertEqual(reservation.state, 'draft')
        reservation.state_draft()
        self.assertEqual(reservation.state, 'draft')
        reservation.state_canceled()
        self.assertEqual(reservation.state, 'canceled')
        reservation.state_validated()
        self.assertEqual(reservation.state, 'validated')
        reservation.state_draft()
        self.assertEqual(reservation.state, 'draft')
        reservation.state_confirm() # Here the reservation is OK, pass the checks
        self.assertEqual(reservation.state, 'validated')

    def test_availability_24_7(self):
        """ Test reservation with availability 24/7 """
        self.resource.availability_24_7 = True
        self.resource.timetable_ids.unlink()
        self.assertTrue(self.resource.availability_24_7)
        reservation = self.res_obj.create(self.data)
        reservation.state_confirm()
        self.assertEqual(reservation.state, 'validated')


    def test_state_rejected(self):
        """ Tests state rejected """
        self.data['resource_id'] = self.resource_val.id
        reservation = self.res_obj.create(self.data)
        self.assertEqual(reservation.state, 'draft')
        reservation.state_confirm()
        self.assertEqual(reservation.state, 'confirmed')
        # We may have called the wizard here
        reservation.write({'state': 'rejected', 'rejection_reason': 'Reason'})
        self.assertEqual(reservation.state, 'rejected')
        self.assertEqual(reservation.rejection_reason, 'Reason')

    def test_confirm_access(self):
        """ Test that only golem_manager can confirm or reject reservation """
        self.data['resource_id'] = self.resource_val.id
        reservation = self.res_obj.create(self.data)
        self.assertEqual(reservation.state, 'draft')
        reservation.state_confirm()
        reservation.state_validated() # OK there, as admin is GOLEM Manager
        reservation.state_canceled()
        reservation.state_draft()
        reservation.state_confirm()
        # Removes group GOLEM manager from current user
        group_manager = self.env.ref('golem_base.group_golem_manager')
        self.env.user.groups_id = [(2, group_manager.id, False)]
        with self.assertRaises(ValidationError) as err:
            reservation.state_validated()
        self.assertIn(u'do not have permissions to validate', err.exception.args[0])

    def test_confirmed_period(self):
        """ Test allowed period """
        self.data['date_start'] = '2012-02-05 11:00:00' # Out of period
        reservation = self.res_obj.create(self.data)
        with self.assertRaises(ValidationError) as err:
            reservation.state_confirm()
            self.assertIn(u'pas disponible durant cette période', err.exception.args[0])

    def test_confirmed_allowed_day(self):
        """ Test allowed day """
        self.data['date_start'] = '2018-02-04 11:00:00' # Bad day
        reservation = self.res_obj.create(self.data)
        with self.assertRaises(ValidationError) as err:
            reservation.state_confirm()
        self.assertIn('not available this day', err.exception.args[0])

    def test_multidays_reservation(self):
        """ Test multidays reservation """
        #two days allowed reservation
        self.data['date_start'] = '2018-02-07 14:00:00' # Wednesday : allowed FROM 7
        self.data['date_stop'] = '2018-02-08 11:00:00' # Thursday : allowed
        reservation = self.res_obj.create(self.data)
        reservation.state_confirm()
        self.assertEqual(reservation.state, 'validated')
        reservation.state_draft()
        #Two days allowed but one not allowed in the middle
        reservation.write({'date_start': '2018-02-06 14:00:00',
                           'date_stop': '2018-02-08 11:00:00'})
        with self.assertRaises(ValidationError) as err:
            reservation.state_confirm()
        self.assertIn('not available during this period', err.exception.args[0])

    def test_confirmed_allowed_hours(self):
        """ Test allowed hours """
        self.data['date_stop'] = '2018-02-05 14:00:00' # Out of range stop hour
        reservation = self.res_obj.create(self.data)
        with self.assertRaises(ValidationError) as err:
            reservation.state_confirm()
            self.assertIn(u'merci de choisir d\'autres horaires', err.exception.args[0])
        # Out of range start hour
        reservation = self.res_obj.create({'resource_id': self.resource.id,
                                           'date_start': '2018-02-05 05:00:00',
                                           'date_stop': '2018-02-05 12:00:00',
                                           'partner_id': self.partner.id})
        with self.assertRaises(ValidationError) as err:
            reservation.state_confirm()
        self.assertIn(u'the resource is not available during this period', err.exception.args[0])

    def test_confirmed_other_res(self):
        """ Test if there are other reservations in conflict """
        reservation = self.res_obj.create(self.data)
        reservation.state_confirm()
        reservation2 = self.res_obj.create({
            'resource_id': self.resource.id,
            'date_start': '2018-02-05 10:00:00',
            'date_stop': '2018-02-05 11:00:00',
            'partner_id': self.partner.id
            })
        reservation2.state_confirm()
        reservation3 = self.res_obj.create({
            'resource_id': self.resource.id,
            'date_start': '2018-02-05 11:20:00',
            'date_stop': '2018-02-05 11:40:00',# Conflict with 2nd res
            'partner_id': self.partner.id
            })
        with self.assertRaises(ValidationError) as err:
            reservation3.state_confirm()
        self.assertIn(u'the resource is already taken', err.exception.args[0])
