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

{
    'name': 'GOLEM Family Memberships',
    'summary': 'GOLEM Family Membership Management',
    'description': 'GOLEM Family Membership Management',
    'version': '10.0.0.1.4',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois, Youssef ELOUAHBY',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['golem_family', 'membership', 'golem_member_minor'],
    'data': ['views/membership_views.xml',
             'views/golem_family_views.xml',
             'wizard/golem_membership_invoice_views.xml']
}
