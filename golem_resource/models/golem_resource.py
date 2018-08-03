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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResource(models.Model):
    """ GOLEM Resource Model """
    _name = 'golem.resource'
    _description = 'GOLEM Resource Model'
    _inherit = 'mail.thread'
    _order = 'name asc'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    validation_required = fields.Boolean(default=False,
                                         string='Is validation required ?')
    type_id = fields.Many2one('golem.resource.type',
                              index=True, string='Resource Type')
    supervisor_id = fields.Many2one('res.partner', index=True, string='Supervisor')
    product_tmpl_id = fields.Many2one('product.template', index=True,
                                      string='Linked product',
                                      help='A generic product can be linked, in '
                                      'order to sell reservations (work in '
                                      'progress)')

    availability_start = fields.Date(required=True, string='Availability start date')
    availability_stop = fields.Date(required=True, string='Availability stop date')
    availability_24_7 = fields.Boolean(string='24/7 availability')
    timetable_ids = fields.One2many('golem.resource.timetable', 'resource_id',
                                    string='Availability timetable')
    reservation_ids = fields.One2many('golem.resource.reservation', 'resource_id',
                                      string='Reservations')
    reservation_count = fields.Integer(compute='_compute_reservation_count')

    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for resource in self:
            resource.reservation_count = len(resource.reservation_ids)

    @api.multi
    def reservation_calendar(self):
        """ current resource reservation calendar """
        self.ensure_one()
        return {
            'name': _('Resource Reservation'),
            'view_mode': 'calendar,tree,form',
            'res_model': 'golem.resource.reservation',
            'context': {'search_default_resource_id': self[0].id},
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def reserveration_list(self):
        """ current resource reservation list """
        self.ensure_one()
        return {
            'name': _('Resource Reservation list'),
            'view_mode': 'tree,form,calendar',
            'res_model': 'golem.resource.reservation',
            'context': {'search_default_resource_id': self[0].id},
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def active_toggle(self):
        """ Toggles active boolean """
        for resource in self:
            resource.active = not resource.active

    @api.constrains('availability_start', 'availability_stop')
    def _check_date_consistency(self):
        """ Checks date consistency """
        for resource in self:
            if resource.availability_stop <= resource.availability_start:
                raise ValidationError(_('End availability should be after than '
                                        'start availability'))
