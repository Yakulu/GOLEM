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

""" Res Partner adaptations """

from odoo import models, fields

class ResPartner(models.Model):
    """ Res Partner adaptations """
    _inherit = 'res.partner'

    is_default_gardian = fields.Boolean()

    def do_default_gardian(self):
        """ make only default gardian """
        self.ensure_one()
        self.is_default_gardian = True
        member_id = self._context.get('member_id', False)
