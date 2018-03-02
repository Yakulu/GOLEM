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

from odoo.tests.common import TransactionCase
from odoo.models import ValidationError


class TestGolemActivity(TransactionCase):

    def setUp(self):
        super(TestGolemActivity, self).setUp()
        self.season = self.env['golem.season'].sudo().create({'name': u'Season 1'})
        type_id = self.ref("golem_activity.golem_activity_type_activity")
        #self.activity = self.env['golem.activity'].create({'name': u'Activity 1',
        #                                                   'season_id': self.season,
        #                                                   'categ_id': categ})
        self.data = {
            'name': u'Activity 1',
            'season_id': self.season.id,
            'type_id': type_id
        }
        self.activity_obj = self.env['golem.activity']
    def test_activity_creation(self):
        """ Test creation of activity """
        activity = self.activity_obj.create(self.data)
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)
        self.assertEqual(activity.queue_activity_number, 0)
