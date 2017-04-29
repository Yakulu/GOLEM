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

from odoo.tests.common import TransactionCase
from odoo.models import ValidationError


class GolemActivityTestCase(TransactionCase):

    def setUp(self):
        super(GolemActivityTestCase, self).setUp()

        self.season_model = self.env['golem.season'].sudo()
        season_data = {'name': u'Current', 'date_start': '2010-01-01',
                       'date_end': '2010-12-31'}
        self.season_current = self.season_model.create(season_data)
        self.activity_model = self.env['golem.activity'].sudo()

    def test_activity_creation(self):
        """ Test creation of activity and periods """
        categ = self.ref('golem_activity.golem_product_category_activities')
        adata = {'name': 'a1', 'season_id': self.season_current.id,
                 'categ_id': categ}
        a1 = self.activity_model.create(adata)
        a1.onchange_season_dates()
        self.assertEqual(a1.name, 'a1')
        self.assertEqual(a1.date_start, self.season_current.date_start)
        self.assertEqual(a1.date_end, self.season_current.date_end)
        self.assertTrue(a1.is_current)
        adata.update({'name': 'a2', 'date_start': '2010-01-01',
                      'date_end': '2009-12-01'})
        with self.assertRaises(ValidationError):
            self.activity_model.create(adata)
