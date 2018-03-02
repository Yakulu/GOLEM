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

""" GOLEM member testing """

from odoo import exceptions
from odoo.tests.common import TransactionCase
# from psycopg2 import IntegrityError


class TestGolemMember(TransactionCase):
    """ GOLEM member testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap member """
        super(TestGolemMember, self).setUp(*args, **kwargs)
        self.data1 = {'lastname': u'LAST1', 'firstname': u'First1'}
        self.data2 = {'lastname': u'LAST2', 'firstname': u'First2'}
        self.data3 = {'lastname': u'LAST3', 'firstname': u'First3'}
        self.member1 = self.env['golem.member']
        self.member2 = self.env['golem.member']
        self.member3 = self.env['golem.member']

    def test_member_creation(self):
        """ Test member creation """
        member1 = self.member1.create(self.data1)
        self.assertFalse(member1.activity_queue_ids)

        """
        self.member2 = mcrt({'lastname': u'LAST', 'firstname': u'Young'})
        self.season = self.env['golem.season'].sudo().create({'name': u'Season 1'})
        self.data = {
            'name': u'Activity 1',
            'season_id': self.season.id,
            'type_id': type_id
        }


        super(TestGolemMember, self).setUp(*args, **kwargs)
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
                             """
