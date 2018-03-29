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

""" GOLEM Resource Packs """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourcePack(models.Model):
    """ GOLEM Resource Pack Model """
    _name = 'golem.resource.pack'
    _description = 'GOLEM Resource Pack Model'

    name = fields.Char()#compute='_compute_name', store=True)
    reservation_ids = fields.One2many('golem.resource.reservation', 'pack_id')

    note = fields.Text(help='Notes, optional subject for the reservation, reason')

    user_id = fields.Many2one('res.users', required=True, index=True, readonly=True,
                              string='User', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='On behalf of',
                                 required=True, index=True)
    state = fields.Selection([('canceled', 'Canceled'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('validated', 'Validated'),
                              ('rejected', 'Rejected')],
                             default='draft')

    @api.multi
    def state_confirm(self):
        for pack in self:
            pack.reservation_ids.state_confirm()
