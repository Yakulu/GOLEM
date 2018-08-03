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
    'name': 'GOLEM Activity Registration Custom Price',
    'summary': 'GOLEM Activity Registration Custom Price',
    'description': '''GOLEM Activity Registration Custom Price :
    - allow set of 1:n slices based on family quotient ;
    - allow set 1:n area data ;
    - allow set price per area and slice ;
    - computes automatically applicable price ;
    - anticipate ruleset to be implemented for computing.''',
    'version': '10.0.0.1.0',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['golem_activity_registration_payment',
                'golem_member_familyquotient'],
    'data': ['security/ir.model.access.csv',
             'views/golem_payment_rule_quotient_slice_views.xml',
             'views/golem_member_views.xml',
             'views/golem_activity_views.xml',
             'wizard/golem_activity_registration_invoicing_views.xml']
}
