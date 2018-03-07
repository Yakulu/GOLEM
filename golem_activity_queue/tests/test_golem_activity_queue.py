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
        """ Bootstrap ActivityQueue """
        super(TestGolemActivityQueue, self).setUp(*args, **kwargs)

        self.season = self.env['golem.season'].create({'name': u'Season 1'})
        self.data_member_1 = {'lastname': u'LAST1',
                              'firstname': u'First1',
                              'season_ids':[(4, self.season.id, False)]}
        self.data_member_2 = {'lastname': u'LAST2',
                              'firstname': u'First2',
                              'season_ids':[(4, self.season.id, False)]}
        self.member = self.env['golem.member']
        type_id = self.env.ref('golem_activity.golem_activity_type_activity')
        self.data_activity = {
            'name': u'Activity 1',
            'season_id': self.season.id,
            'type_id': type_id.id
        }
        self.activity = self.env['golem.activity']
        self.activity_queue = self.env['golem.activity.queue']
        self.activity_registration = self.env['golem.activity.registration']

    def test_activity_queue_basic(self):
        """ Test activity queue basics """
        member1 = self.member.create(self.data_member_1)
        activity = self.activity.create(self.data_activity)
        activity.auto_registration_from_queue = False
        activity_queue = self.activity_queue.create({'activity_id': activity.id,
                                                     'member_id': member1.id})
        self.assertEqual(activity.activity_queue_ids[0], activity_queue)
        self.assertEqual(member1.activity_queue_ids[0], activity_queue)

    def test_check_member_registration(self):
        """ Test activity queue fordib if already in activity """
        member1 = self.member.create(self.data_member_1)
        activity = self.activity.create(self.data_activity)
        self.activity_registration.create({'activity_id': activity.id,
                                           'member_id': member1.id})
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        with self.assertRaises(ValidationError) as err:
            self.activity_queue.create({'activity_id': activity.id,
                                        'member_id': member1.id})
        self.assertIn('already registered for this activity', err.exception.args[0])
