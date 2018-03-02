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

""" GOLEM Activity Queue testing """

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestGolemActivityQueue(TransactionCase):
    """ GOLEM Activity Queue testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource """
        super(TestGolemActivityQueue, self).setUp(*args, **kwargs)

        self.season = self.env['golem.season'].sudo().create({'name': u'Season 1'})
        type_id = self.ref("golem_activity.golem_activity_type_activity")
        print "_______________________"
        print self.season
        print type_id
        self.activity = self.env['golem.activity'].create({'name': u'Activity 1',
                                                           'season_id': self.season.id,
                                                           'type_id': type_id})
        self.member = self.env['golem.member'].create({
            'lastname': u'LAST',
            'firstname': u'First'
        })
        self.data = {
            'activity_id': self.activity.id,
            'member_id': self.member.id,
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01'
        }
        self.activity_queue_obj = self.env['golem.activity.queue']

    def test_activity_queue_basic(self):
        """ Test activity queue bases """
        activity_queue = self.activity_queue_obj.create(self.data)
        self.assertEqual(activity_queue.member_id, self.member)
        self.assertEqual(activity_queue.activity_id, self.activity)
        self.assertEqual(activity_queue.activity_id.activity_queue_ids[0], activity_queue)
        self.assertEqual(activity_queue.places_remain, self.activity.places_remain)
