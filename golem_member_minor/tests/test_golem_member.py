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


class GolemMemberMinorTestCase(TransactionCase):

    def setUp(self):
        super(GolemMemberMinorTestCase, self).setUp()
        season_mdl = self.env['golem.season'].sudo()
        self.season_current = season_mdl.create({'name': u'Current'})
        self.member_model = self.env['golem.member'].sudo()

    def test_member_minor(self):
        """ Test minor computing """
        m = self.member_model.create({'lastname': u'Doe', 'firstname': u'Joe'})
        self.assertFalse(m.is_minor)
        m = self.member_model.create({'lastname': u'Doe', 'firstname': u'Bob',
                                      'birthdate_date': '1990-01-01'})
        self.assertFalse(m.is_minor)
        m.write({'birthdate_date': '2015-01-01'})
        self.assertTrue(m.is_minor)
