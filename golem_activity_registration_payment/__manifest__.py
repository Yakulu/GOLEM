# -*- coding: utf-8 -*-

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
    'name': 'GOLEM Activity Member Registration Payments',
    'summary': 'GOLEM Activities Member Registration Payments',
    'description': 'GOLEM Activities Member Registration Payments',
    'version': '10.0.0.3.5',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['golem_activity_registration_state', 'golem_payment'],
    'data': ['views/golem_member_views.xml',
             'views/golem_activity_registration_views.xml',
             'report/golem_member_card_templates.xml',
             'wizard/golem_activity_registration_invoicing.xml']
}
