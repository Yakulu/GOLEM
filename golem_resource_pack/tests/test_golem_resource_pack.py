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

""" GOLEM Resource Pack testing """

import logging
from odoo.tests.common import TransactionCase
_LOGGER = logging.getLogger(__name__)


class TestGolemResourcePack(TransactionCase):
    """ GOLEM Resource Reservation testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource Reservation """
        super(TestGolemResourcePack, self).setUp(*args, **kwargs)

        self.resource = self.env['golem.resource'].create({
            'name': 'Resource',
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01',
            'availibility_24_7': True
        })
        self.resource_val = self.env['golem.resource'].create({
            'name': 'Resource to validate',
            'avaibility_start': '2018-01-01',
            'avaibility_stop': '2020-01-01',
            'validation_required': True,
            'availibility_24_7': True
        })

        self.partner = self.env['res.partner'].create({'firstname': 'John',
                                                       'lastname': 'DOE',
                                                       'is_company': False})

        reservation_obj = self.env['golem.resource.reservation']
        self.reservation_1 = reservation_obj.create({
            'resource_id': self.resource.id,
            'date_start': '2018-02-05 11:00:00',
            'date_stop': '2018-02-05 12:00:00',
            'partner_id': self.partner.id
        })
        self.reservation_2 = reservation_obj.create({
            'resource_id': self.resource.id,
            'date_start': '2018-02-06 11:00:00',
            'date_stop': '2018-02-06 12:00:00',
            'partner_id': self.partner.id
        })
        self.reservation_3 = reservation_obj.create({
            'resource_id': self.resource_val.id,
            'date_start': '2018-02-05 11:00:00', # is monday
            'date_stop': '2018-02-05 12:00:00',
            'partner_id': self.partner.id
        })
        self.pack_obj = self.env['golem.resource.pack']
        self.pack_data = {
            'name': 'Pack Test',
            'partner_id': self.partner.id
        }


    def test_pack_basic(self):
        """ Test pack bases """
        pack = self.pack_obj.create(self.pack_data)
        self.assertFalse(pack.reservation_ids)
        self.assertFalse(self.reservation_1.pack_id)
        pack.reservation_ids = [(4, self.reservation_1.id, 0),
                                (4, self.reservation_2.id, 0)]
        self.assertEqual(pack.reservation_ids[0].state, "draft")
        self.assertEqual(self.reservation_1.pack_id.id, pack.id)
        self.assertEqual(pack.state, "draft")
        self.assertEqual(pack.reservation_count, 2)
        #confirm pack ==> all validated
        pack.state_confirm()#no validation required
        self.assertEqual(pack.reservation_ids[0].state, "validated")
        self.assertEqual(pack.state, "validated")
        #pack draft ==> all draft
        pack.state_draft()
        self.assertEqual(pack.reservation_ids[0].state, "draft")
        self.assertEqual(pack.state, "draft")
        # confirm pack and draft reservation ==> pack draft
        pack.state_confirm()
        pack.reservation_ids[0].state_draft()
        self.assertEqual(pack.reservation_ids[0].state, "draft")
        self.assertEqual(pack.state, "draft")
        #confirm reservation ==> pack validated
        pack.reservation_ids[0].state_confirm()
        self.assertEqual(pack.reservation_ids[0].state, "validated")
        self.assertEqual(pack.state, "validated")
        pack.reservation_ids = [(5, 0, 0)]
        self.assertFalse(pack.reservation_ids)
        self.assertEqual(pack.reservation_count, 0)


    def test_pack_validation(self):
        """ Test pack validation """
        pack = self.pack_obj.create(self.pack_data)
        self.assertFalse(pack.reservation_ids)
        self.assertFalse(self.reservation_1.pack_id)
        pack.reservation_ids = [(4, self.reservation_1.id, 0),
                                (4, self.reservation_3.id, 0)]
        self.assertEqual(pack.reservation_ids[0].state, "draft")
        self.assertEqual(self.reservation_1.pack_id.id, pack.id)
        self.assertEqual(pack.state, "draft")
        pack.state_confirm()#validation required
        self.assertEqual(pack.state, "confirmed")
        pack.state_validated()
        self.assertEqual(pack.state, "validated")
        self.assertEqual(pack.reservation_ids[0].state, "validated")
        self.assertEqual(pack.reservation_ids[1].state, "validated")

    def test_pack_rejection(self):
        """ test pack rejection """
        pack = self.pack_obj.create(self.pack_data)
        self.assertFalse(pack.reservation_ids)
        self.assertFalse(self.reservation_1.pack_id)
        pack.reservation_ids = [(4, self.reservation_1.id, 0),
                                (4, self.reservation_3.id, 0)]
        self.assertEqual(pack.reservation_ids[0].state, "draft")
        self.assertEqual(self.reservation_1.pack_id.id, pack.id)
        self.assertEqual(pack.state, "draft")
        pack.state_confirm()#validation required
        rej_wizard = self.env['golem.pack.rejection.wizard'].create({
            'pack_id': pack.id,
            'reason' : 'reason1'
        })
        rej_wizard.reject()
        self.assertEqual(pack.state, "rejected")
        self.assertEqual(self.reservation_3.state, "rejected")
        self.assertEqual(pack.rejection_reason, 'reason1')
