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

""" GOLEM Resources management """

from odoo import models, fields, api

class GolemReservationRejectionWizard(models.TransientModel):
    """GOLEM Resource wizard : refusal reason for a reservation """
    _name = "golem.reservation.rejection.wizard"

    reservation_id = fields.Many2one('golem.resource.reservation', required=True)
    reason = fields.Text(required=True)

    @api.multi
    def reject(self):
        """ Sets reservation status to rejected and add reason """
        self.ensure_one()
        rejection = self[0]
        rejection.reservation_id.write({'state': 'rejected',
                                        'rejection_reason': rejection.reason})
