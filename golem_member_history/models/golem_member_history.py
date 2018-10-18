# -*- coding: utf-8 -*-

#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

""" GOLEM Member History Management """

from odoo import models, fields, api, _

class GolemMemberHistory(models.Model):
    """ GOLEM Member History """
    _name = 'golem.member.history'
    _description = 'GOLEM Member History Management'
    _order = "season_id desc, id desc"

    member_id = fields.Many2one('golem.member', required=True, auto_join=True,
                                ondelete="cascade")
    season_id = fields.Many2one('golem.season', required=True, auto_join=True,
                                ondelete="cascade")
    gender = fields.Selection([('male', _('Male')), ('female', _('Female'))])
    area_id = fields.Many2one('golem.partner.area', string='Area', ondelete="cascade")
    city = fields.Char()
    family_quotient = fields.Monetary()
    currency_id = fields.Many2one(related="member_id.currency_id", string="Currency", readonly=True)
    pcs_id = fields.Many2one('golem.pcs', string='PCS')
    nationality_id = fields.Many2one('res.country', string="Nationality", ondelete="cascade")
