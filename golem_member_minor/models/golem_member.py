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

""" GOLEM Member Minor management """

from datetime import datetime, timedelta
from odoo import models, fields, api

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    ADULT_DURATION = timedelta(days=365*18)
    legal_guardian_ids = fields.Many2many(
        'res.partner', string='Legal guardians', index=True,
        domain="['&', ('is_company', '=', False), ('id', '!=', partner_id)]")
    activities_participation = fields.Boolean('Activities participation?')
    is_minor = fields.Boolean('Is minor?', compute='_compute_is_minor',
                              store=True, default=False)

    @api.multi
    @api.depends('birthdate_date')
    def _compute_is_minor(self):
        for member in self:
            if member.birthdate_date:
                member.is_minor = ((datetime.now() - self.ADULT_DURATION) <
                                   fields.Datetime.from_string(member.birthdate_date))
            else:
                member.is_minor = False
