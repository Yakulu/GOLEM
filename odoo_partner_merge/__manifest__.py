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

{
    'name': 'Odoo spinoff partner merger from CRM',
    'summary': 'Odoo spinoff partner merger from CRM',
    'description': 'Odoo spinoff partner merger from CRM (wizard, mainly)',
    'version': '10.0.1.0.0',
    'category': 'GOLEM',
    'author': 'Odoo SA, Fabien Bourgeois',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': ['base'],
    'data': ['wizard/base_partner_merge_views.xml']
}
