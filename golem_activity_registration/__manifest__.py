# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
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
    'name': 'GOLEM Activity Member Registrations',
    'summary': 'GOLEM Activities Member Registrations management',
    'version': '10.0.1.4.2',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois, Michel Dessenne',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['golem_activity', 'golem_member'],
    'data': ['views/golem_activity_registration_views.xml',
             'views/golem_member_views.xml',
             'views/golem_activity_views.xml',
             'report/golem_member_card_templates.xml',
             'security/ir.model.access.csv',
             'report/golem_activity_report_templates.xml']
}
