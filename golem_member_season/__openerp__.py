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

{
    'name': 'GOLEM members seasons',
    'summary': 'GOLEM non-profit members seasons glue code',
    'description': ''' Link between GOLEM members and seasons, with
    management of number code linked to season ''',
    'version': '0.1',
    'category': 'Non-profit management',
    'author': 'Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': ['golem_member', 'golem_season'],
    'data': ['views/golem_member_season_view.xml']
}
