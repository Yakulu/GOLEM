# -*- coding: utf-8 -*-

#    Copyright 2016 Fabien Bourgeois <fabien@yaltik.com>
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

from openerp import exceptions
from openerp.tests.common import TransactionCase
# from psycopg2 import IntegrityError


class GolemMemberTestCase(TransactionCase):

    def setUp(self):
        super(GolemMemberTestCase, self).setUp()
        self.member_numberconfig_model = self.env['golem.member.numberconfig']
        season_mdl = self.env['golem.season'].sudo()
        self.season_current = season_mdl.create({'name': u'Current'})
        self.season_current.do_default_season()
        self.season_next = season_mdl.create({'name': u'Next'})
        self.member_model = self.env['golem.member'].sudo()
        mcrt = self.member_model.create
        self.member1 = mcrt({'lastname': u'LAST', 'firstname': u'First'})
        self.member2 = mcrt({'lastname': u'LAST', 'firstname': u'Young',
                             'birthdate_date': '2016-01-01'})

    def test_member_creation_noname(self):
        """ Test creation of member without needed parameters """
        with self.assertRaises(exceptions.ValidationError) as cm:
            self.member_model.create({})
        self.assertIn('Error(s) with partner', cm.exception.args[0])
        self.assertEqual('No name is set.', cm.exception.args[1])

    def test_current_season(self):
        """ Test if default season if fixed according to setUp and if users
        are correctly seen """
        self.assertEqual(self.member_model._default_season(),
                         self.season_current)
        self.assertTrue(self.member1.is_current)
        self.assertTrue(self.member2.is_current)
        self.season_next.do_default_season()
        self.assertFalse(self.member1.is_current)
        self.assertFalse(self.member2.is_current)

    def test_member_numbers_manual(self):
        """ Tests manual member number generation """
        conf = self.member_numberconfig_model.create({'is_automatic': '0'})
        conf.apply_recompute()
        self.assertFalse(self.member1.number)
        self.member1.number_manual = u'M01'
        self.assertEqual(self.member1.number_manual, self.member1.number)
        # **Can not test IntegrityError without Odoo ERROR...**
        # with self.assertRaises(IntegrityError) as cm:
        #     self.member2.number_manual = u'M01'
        # self.assertIn('duplicate key value violates unique constraint',
        #               cm.exception.args[0])

    def test_member_numbers_auto_perseason(self):
        """ Tests per season automatic member number generation + prefix """
        conf = self.member_numberconfig_model.create({'is_automatic': '1',
                                                      'is_per_season': '1',
                                                      'prefix': u'M'})
        conf.apply_recompute()
        self.assertEqual(self.member1.number, u'M1')
        self.assertEqual(self.member2.number, u'M2')
        self.member2.season_ids += self.season_next
        self.assertEqual(self.member2.number, u'M2')
        self.season_next.do_default_season()
        self.assertEqual(self.member2.number, u'M1')
        self.assertFalse(self.member1.number)

    def test_member_numbers_auto_global(self):
        """ Tests global automatic member number generation """
        conf = self.member_numberconfig_model.create({'is_automatic': '1',
                                                      'is_per_season': '0'})
        conf.apply_recompute()
        self.assertEqual(self.member1.number, u'1')
        self.assertEqual(self.member2.number, u'2')
        new_m = self.member_model.create({'lastname': 'NEW',
                                          'firstname': 'Buddy',
                                          'season_ids': [self.season_next]})
        self.assertEqual(new_m.number, u'3')
