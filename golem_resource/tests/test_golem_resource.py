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

""" GOLEM Resource testing """

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestGolemResource(TransactionCase):
    """ GOLEM Resource testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource """
        super(TestGolemResource, self).setUp(*args, **kwargs)
        self.data = {
            'name': 'Resource',
            'availability_start': '2018-01-01',
            'availability_stop': '2020-01-01'
        }
        self.resource_obj = self.env['golem.resource']

    def test_resource_basic(self):
        """ Test resource bases """
        resource = self.resource_obj.create(self.data)
        self.assertTrue(resource.active)
        self.assertFalse(resource.validation_required)
        self.assertEqual(resource.availability_start, '2018-01-01')
        self.assertEqual(resource.availability_stop, '2020-01-01')
        self.assertFalse(resource.supervisor_id)
        self.assertFalse(resource.product_tmpl_id)
        self.assertFalse(resource.timetable_ids)
        self.assertFalse(resource.reservation_ids)

    def test_resource_active(self):
        """ Test resource active """
        resource = self.resource_obj.create(self.data)
        self.assertTrue(resource.active)
        resource.active_toggle()
        self.assertFalse(resource.active)
        resource.active_toggle()
        self.assertTrue(resource.active)

    def test_resource_dates(self):
        """ Test resource dates : stop can not be after start """
        self.data.update({'availability_stop': '2017-01-01'})
        with self.assertRaises(ValidationError):
            self.resource_obj.create(self.data)

    def test_resource_dates_equal(self):
        """ Test resource dates : stop can not be equal to start """
        self.data.update({'availability_stop': self.data['availability_start']})
        with self.assertRaises(ValidationError):
            self.resource_obj.create(self.data)
