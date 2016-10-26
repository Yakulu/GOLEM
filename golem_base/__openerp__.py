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
    'name': 'GOLEM base module for global dependencies',
    'summary': 'GOLEM base installs base and shared dependencies for GOLEM',
    'version': '8.0.1.0.0',
    'category': 'GOLEM',
    'author': 'Fabien Bourgeois',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': ['membership', 'contacts', 'mail', 'account_voucher',
                'partner_firstname', 'partner_contact_birthdate',
                'partner_contact_gender', 'partner_contact_nationality',
                'l10n_fr', 'l10n_fr_state', 'l10n_fr_department',
                'l10n_fr_tax_sale_ttc', 'l10n_fr_siret',
                'web_widget_phone_check_fr', 'web_widget_email_check',
                'web_widget_url_check', 'web_one2many_kanban',
                'yaltik_backend_theme'],
    'data': ['security/golem_security.xml']
}
