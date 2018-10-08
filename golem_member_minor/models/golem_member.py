# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

from datetime import date, timedelta
from odoo import models, fields, api

ADULT_DURATION = timedelta(days=365.25*18)

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    legal_guardian_ids = fields.Many2many(
        'res.partner', string='Legal guardians', index=True, auto_join=True,
        domain="['&', ('is_company', '=', False), ('id', '!=', partner_id)]")
    activities_participation = fields.Boolean('Activities participation?')
    leave_alone = fields.Boolean('Can leave alone?')
    is_minor = fields.Boolean('Is minor?', compute='_compute_is_minor',
                              search='_search_is_minor', default=False)

    @api.depends('birthdate_date')
    def _compute_is_minor(self):
        for member in self:
            if member.birthdate_date:
                member.is_minor = ((date.today() - ADULT_DURATION) <
                                   fields.Date.from_string(member.birthdate_date))
            else:
                member.is_minor = False

    def _search_is_minor(self, operator, value):
        """ Search function for is minor """
        today = date.today()
        adult_date = today - ADULT_DURATION
        if operator == '=':
            operator = '>' if value else '<='
        else:
            operator = '<=' if value else '>'
        return [('birthdate_date', operator, adult_date)]

    def membership_invoice_action(self):
        """ Membership invoice action for minor member """
        self.ensure_one()
        member = self[0]
        action = self.env.ref('golem_member.golem_membership_invoice_action').read()[0]
        if member.is_minor:
            action['context'] = {'default_src_member_id': member.id,
                                 'default_partner_id': False}
        return action
