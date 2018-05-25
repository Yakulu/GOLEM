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

""" GOLEM Pack Quick Reservation Wizard """

from datetime import timedelta
from odoo import models, fields, api

class GolemPackQuickReservationWizard(models.TransientModel):
    """ GOLEM Pack Quick Reservation Wizard """
    _name = 'golem.pack.quick.reservation.wizard'
    _description = 'GOLEM Pack Quick Reservation Wizard'

    pack_id = fields.Many2one('golem.resource.pack', required=True,
                              ondelete='cascade')
    partner_id = fields.Many2one(related='pack_id.partner_id')
    resource_ids = fields.Many2many('golem.resource', string="Resource List")

    date_start = fields.Datetime('Start date', required=True)
    date_stop = fields.Datetime('Stop date', required=True)

    @api.onchange('date_start')
    def onchange_date_start(self):
        """ Propose automatically stop hour after start hour had been filled """
        for reservation in self:
            if reservation.date_start:
                start = fields.Datetime.from_string(reservation.date_start)
                duration = timedelta(hours=1)
                reservation.date_stop = start + duration

    @api.multi
    def create_reservations(self):
        """ Create a reservation for each resource """
        self.ensure_one()
        wizard = self[0]
        for resource in wizard.resource_ids:
            self.env['golem.resource.reservation'].create({
                'user_id': self.env.user.id,
                'partner_id': wizard.partner_id.id,
                'resource_id': resource.id,
                'date_start': wizard.date_start,
                'date_stop': wizard.date_stop,
                'pack_id': wizard.pack_id.id
            })
