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
    'name': 'GOLEM non-profit members',
    'summary': 'Extends Odoo contacts for MJC',
    'description': 'Non-profit french MJC members management',
    'version': '0.1',
    'category': 'Non-profit management',
    'author': 'Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': ['contacts',
                'partner_firstname',
                'partner_contact_birthdate',
                'partner_contact_gender',
                'partner_contact_nationality',
                'membership',
                'account_voucher',
                'mail',
                'l10n_fr_state',
                'l10n_fr_department',
                'l10n_fr_tax_sale_ttc',
                'l10n_fr_siret',
                'web_widget_phone_check_fr',
                'web_widget_email_check',
                'web_widget_url_check',
                'golem_season'],
    'data': ['views/golem_member_view.xml', 'views/members_menu.xml',
             'views/number_config.xml', 'data/number_config.xml']
}
