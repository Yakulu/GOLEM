# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Activity Places Tests """

from odoo.tests.common import TransactionCase
from odoo.models import ValidationError


class GolemActivitySessionTestCase(TransactionCase):
    """ GOLEM Activity Places Tests """

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

    def test_session_places_overbook(self):
        """ Test computed places with overbooked on """
        self.session1.places = 4
        self.assertEqual(self.session1.places_used, 0)
        self.assertEqual(self.session1.places_remain, 4)
        self.session1.is_overbooked = True
        self.session1.onchange_is_overbooked()
        self.assertEqual(self.session1.places_overbooked, 5)
        self.assertEqual(self.session1.places_remain, 5)
        self.session1.places_overbooked = 15
        self.assertEqual(self.session1.places_overbooked, 15)
        self.assertEqual(self.session1.places_remain, 15)
        # Overbooked places cannot be < to places
        with self.assertRaises(ValidationError):
            self.session1.places_overbooked = 2
