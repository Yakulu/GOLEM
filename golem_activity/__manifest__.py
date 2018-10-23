# -*- coding: utf-8 -*-

#    Copyright 2016-2018 Fabien Bourgeois <fabien@yaltik.com>
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
    'name': 'GOLEM activities',
    'summary': 'Extends Odoo products for multi-activity',
    'description': 'Extends Odoo products for multi-activity',
    'version': '10.0.2.6.1',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois, Michel Dessenne',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': ['product', 'account', 'golem_base', 'golem_season'],
    'data': ['security/ir.model.access.csv',
             'data/golem_activity_data.xml',
             'views/golem_activity_views.xml',
             'report/golem_activity_report_templates.xml',
             'views/res_partner_views.xml']
}
