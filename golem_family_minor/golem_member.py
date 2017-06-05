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

""" GOLEM Family Minor glue module"""

from odoo import models, fields

LEGAL_DMN = "['&', ('family_id', '=', family_id), ('id', '!=', partner_id)]"


class GolemMember(models.Model):
    """ Member adaptations """
    _inherit = 'golem.member'

    legal_guardian_ids = fields.Many2many(domain=LEGAL_DMN)
