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

""" GOLEM Activity testing """

from odoo.tests.common import TransactionCase


class TestGolemActivity(TransactionCase):
    """ GOLEM Activity Queue testing """

    def setUp(self):
        """ Bootstrap activity """
        super(TestGolemActivity, self).setUp()
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
        self.activity_registration = self.env['golem.activity.registration']
        self.activity_queue = self.env['golem.activity.queue']

    def test_activity_creation(self):
        """ Test activity defaults for queue """
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)
        self.assertEqual(activity.queue_activity_number, 0)
        self.assertFalse(activity.activity_registration_ids)
        self.assertFalse(activity.activity_queue_ids)

    def test_auto_registration_toggle(self):
        """ Test Toggle Autoregistration from queue """
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.auto_registration_from_queue)
        activity.auto_registration_toggle()
        self.assertFalse(activity.auto_registration_from_queue)
        activity.auto_registration_toggle()
        self.assertTrue(activity.auto_registration_from_queue)

    def test_queue_allowed_toggle(self):
        """ Test Toggle queue_allowed """
        #création de 2 membre est une activité
        member1 = self.member.create(self.data_member_1)
        member2 = self.member.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        registration_data = {'activity_id' : activity.id, 'member_id' : member1.id}
        queue_data = {'activity_id' : activity.id, 'member_id' : member2.id}

        self.assertTrue(activity.queue_allowed)
        activity.places = 1
        self.activity_registration.create(registration_data)
        self.activity_queue.create(queue_data)

        self.assertTrue(activity.auto_registration_from_queue)
        activity.queue_allowed_toggle()
        self.assertFalse(activity.queue_allowed)
        self.assertFalse(activity.activity_queue_ids)

        queue_activate_wizard_model = self.env['golem.activity.automated.queue.activate.wizard']
        queue_activate_wizard = queue_activate_wizard_model.create({'activity_id': activity.id})
        queue_activate_wizard.activate_queue()
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)

    def test_auto_registration(self):
        """ Test auto registration from queue """
        member1 = self.member.create(self.data_member_1)
        member2 = self.member.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)

        registration_data = {'activity_id' : activity.id, 'member_id' : member1.id}
        queue_data = {'activity_id' : activity.id, 'member_id' : member2.id}

        activity.places = 1
        registration = self.activity_registration.create(registration_data)
        self.activity_queue.create(queue_data)
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        self.assertEqual(activity.activity_queue_ids[0].member_id, member2)

        registration.unlink()
        self.assertEqual(activity.activity_registration_ids[0].member_id, member2)
        self.assertFalse(activity.activity_queue_ids)

    def test_delete_queue_member(self):
        """ Test Delete Queue member if they directly register """
        member1 = self.member.create(self.data_member_1)
        member2 = self.member.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)
        activity.auto_registration_toggle()
        self.assertFalse(activity.auto_registration_from_queue)

        registration_data = {'activity_id' : activity.id, 'member_id' : member1.id}
        queue_data = {'activity_id' : activity.id, 'member_id' : member2.id}

        activity.places = 1
        registration = self.activity_registration.create(registration_data)
        self.activity_queue.create(queue_data)
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        self.assertEqual(activity.activity_queue_ids[0].member_id, member2)
        registration.unlink()

        activity.activity_registration_ids = [(0, False, queue_data)]
        self.assertFalse(activity.activity_queue_ids)
        self.assertEqual(activity.activity_registration_ids[0].member_id, member2)
