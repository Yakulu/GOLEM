# -*- coding: utf-8 -*-

#    Copyright 2016-2018 Fabien Bourgeois <fabien@yaltik.com>
#    Copyright 2018 Michel Dessenne <michel@yaltik.com>

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
    'name': 'GOLEM non-profit members',
    'summary': 'Extends Odoo contacts for MJC',
    'description': 'Extends Odoo contacts for MJC',
    'version': '10.0.2.2.1',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois, Michel Dessenne',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': ['golem_base', 'golem_membership', 'golem_activity',
                'golem_season', 'odoo_partner_merge'],
    'data': ['views/golem_member_views.xml',
             'views/res_partner_views.xml',
             'views/golem_member_numberconfig_views.xml',
             'report/golem_member_card_templates.xml',
             'data/golem_member_numberconfig_data.xml',
             'security/ir.model.access.csv']
}
