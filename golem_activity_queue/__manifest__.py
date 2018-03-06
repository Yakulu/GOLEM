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
    'name': 'GOLEM activity queues',
    'summary': 'GOLEM activity queues',
    'description': ''' GOLEM activity queue management ''',
    'version': '10.0.1.1.0',
    'category': 'GOLEM',
    'author': 'Youssef El Ouahby, Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': ['golem_activity', 'golem_activity_registration'],
    'data': [
        'security/ir.model.access.csv',
        'views/golem_activity_queue_views.xml',
        'views/golem_activity_views.xml',
        'views/golem_member_views.xml',
        'wizard/golem_activity_queue_choose_views.xml',
        'wizard/golem_activity_automated_queue_activate_views.xml'
    ]
}
