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

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    nationality_id = fields.Many2one('res.country', 'Nationality',
                                     default=_get_default_nationality_id)

    # Gender overwriting : no need for 'other' choice
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])


class GolemMember(models.Model):
    """ GOLEM Member """
    _name = 'golem.member'
    _inherit = 'mail.thread'
    _inherits = {'res.partner': 'partner_id'}

    number = fields.Char('Number', size=50, index=True)
    pictures_agreement = fields.Boolean('Pictures agreement?')
