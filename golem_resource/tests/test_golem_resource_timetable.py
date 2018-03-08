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

""" GOLEM Resource Timetable testing """

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestGolemResourceTimetable(TransactionCase):
    """ GOLEM Resource Timetable testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap timetable """
        super(TestGolemResourceTimetable, self).setUp(*args, **kwargs)
        self.resource = self.env['golem.resource'].create({
            'name': 'Resource',
            'validation_required': False,
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01'
        })
        self.timetable_obj = self.env['golem.resource.timetable']
        self.data = {'resource_id': self.resource.id,
                     'weekday': '0',
                     'time_start': 8.0,
                     'time_stop': 10.0}

    def test_timetable_basic(self):
        """ Test Timetable bases """
        timetable = self.timetable_obj.create(self.data)
        self.assertEqual(timetable.resource_id, self.resource)
        self.assertEqual(timetable.time_start, 8.0)
        self.assertEqual(timetable.time_stop, 10.0)
        self.assertEqual(timetable, self.resource.timetable_ids[0])

    def test_timetable_times(self):
        """ Test timetable times : stop can not be equal or after start """
        self.data.update({'time_stop': 7.0})
        with self.assertRaises(ValidationError):
            self.timetable_obj.create(self.data)
        self.data.update({'time_stop': self.data['time_start']})
        with self.assertRaises(ValidationError):
            self.timetable_obj.create(self.data)
