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

from openerp.tests.common import TransactionCase
from openerp.models import ValidationError
from psycopg2 import IntegrityError


class GolemActivitySessionTestCase(TransactionCase):

    def setUp(self):
        super(GolemActivitySessionTestCase, self).setUp()
        season_model = self.env['golem.season'].sudo()
        season_data = {'name': u'Current', 'date_start': '2010-01-01',
                       'date_end': '2010-12-31'}
        season1 = season_model.create(season_data)
        activity_model = self.env['golem.activity'].sudo()
        categ = self.ref('golem_activity.golem_product_category_activities')
        self.activity1 = activity_model.create({'name': 'activity1',
                                                'default_code': 'A1',
                                                'categ_id': categ,
                                                'season_id': season1.id})
        self.activity1.onchange_season_dates()
        self.session_model = self.env['golem.activity.session'].sudo()
        sdata = {'name': 's1', 'activity_id': self.activity1.id}
        self.session1 = self.session_model.create(sdata)
        self.session1.onchange_activity_id()
        self.member_model = self.env['golem.member'].sudo()

    def test_session_name(self):
        """ Test activity session name computing """
        self.assertEqual(self.session1.default_code,
                         self.activity1.default_code)
        self.assertEqual(self.session1.session_name, u'[A1] s1')

    def test_check_period(self):
        """ Test periods constraints """
        self.session1.write({'is_recurrent': False, 'date_start': '2010-01-10',
                             'date_end': '2010-01-31'})
        # Start after end
        with self.assertRaises(ValidationError):
            self.session1.date_start = '2011-01-15'
        # Start before activity start
        with self.assertRaises(ValidationError):
            self.session1.date_start = '2009-01-15'
            # End after activity end
        with self.assertRaises(ValidationError):
            self.session1.date_end = '2012-01-15'

    def test_session_places_constraint(self):
        """ Test that you cannot fix negative places """
        try:
            self.session1.places = -2
        except IntegrityError as e:
            self.assertIn('violates check constraint', e.args[0])
            self.cr.rollback()

    def test_session_places(self):
        """ Test computed places fields """
        self.session1.places = 1
        self.assertEqual(self.session1.places_remain, 1)
        self.assertEqual(self.session1.places_used, 0)
        m1 = self.member_model.create({'lastname': 'DOE', 'firstname': 'Joe'})
        m2 = self.member_model.create({'lastname': 'DOE', 'firstname': 'Jen'})
        # Member subscription
        self.session1.member_ids = [m1.id]
        self.assertEqual(self.session1.places_remain, 0)
        self.assertEqual(self.session1.places_used, 1)
        # No place anymore
        with self.assertRaises(ValidationError):
            self.session1.member_ids = [m1.id, m2.id]
