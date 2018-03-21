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

""" GOLEM Resource Option Selection"""


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourceOptionSelection(models.Model):
    """ GOLEM Resource Option SelectionModel """
    _name = 'golem.resource.option.selection'
    _description = 'GOLEM Resource option selection Model'

    resource_id = fields.Many2one('golem.resource', 'Resource')
    option_id = fields.Many2one('golem.resource.option', 'Option')
    reservation_id = fields.Many2one('golem.resource.reservation', 'Reservation')

    _sql_constraints = [
        ('unique_selection', "UNIQUE(resource_id, option_id, reservation_id)",
         _("Not allowed, a reservation with same option and resource already exists"))]
