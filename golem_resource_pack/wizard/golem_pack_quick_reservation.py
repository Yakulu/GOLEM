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

from odoo import models, fields, api

class GolemPackQuickReservationWizard(models.TransientModel):
    """GOLEM Pack Quick Reservation Wizard """
    _name = "golem.pack.quick.reservation.wizard"

    pack_id = fields.Many2one('golem.resource.pack', required=True)
    partner_id = fields.Many2one('res.partner', string='On behalf of', readonly=True)
    resource_ids = fields.Many2many('golem.resource', string="Resource List")

    date_start = fields.Datetime('Start date', required=True)
    date_stop = fields.Datetime('Stop date', required=True)


    @api.multi
    def create_reservations(self):
        """ Create a reservation for each resource """
        self.ensure_one()
        wizard = self[0]
        data = []
        for resource in wizard.resource_ids:
            reservation = {'user_id': self.env.user,
                           'partner_id': wizard.partner_id,
                           'resource_id': resource,
                           'date_start': wizard.date_start,
                           'date_stop': wizard.date_stop}
            data.append((0, 0, reservation))
        wizard.pack_id.reservation_ids = data
