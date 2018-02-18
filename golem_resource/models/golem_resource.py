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


class GolemResource(models.Model):
    """ GOLEM Resource Model """
    _name = 'golem.resource'
    _description = 'GOLEM Resource Model'
    _inherit = 'mail.thread'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    validation_required = fields.Boolean(default=True,
                                         string='Is validation required ?')
    type_id = fields.Many2one('golem.resource.type',
                              index=True, string='Resource Type')
    supervisor_id = fields.Many2one('res.partner', index=True, string='Supervisor')
    product_tmpl_id = fields.Many2one('product.template', index=True,
                                      string='Linked product',
                                      help='A generic product can be linked, in '
                                      'order to sell reservations (work in '
                                      'progress)')

    avaibility_start = fields.Date(required=True, string='Availibility start date')
    avaibility_stop = fields.Date(required=True, string='Availibility stop date')
    timetable_ids = fields.One2many('golem.resource.timetable', 'resource_id',
                                    string='Availibility timetable')
    reservation_ids = fields.One2many('golem.resource.reservation', 'resource_id',
                                      string='Reservations')

    @api.multi
    def active_toggle(self):
        """ Toggles active boolean """
        for resource in self:
            resource.active = not resource.active
