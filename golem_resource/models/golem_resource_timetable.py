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

""" GOLEM Resource Timetable """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemTimetable(models.Model):
    """ Golem Timetable """
    _name = "golem.resource.timetable"
    _description = "Golem Timetable"
    _rec_name = 'weekday'
    _order = 'weekday asc,time_start asc'

    resource_id = fields.Many2one('golem.resource', required=True,
                                  string='Linked resource')
    weekday = fields.Selection([('0', _('Monday')),
                                ('1', _('Tuesday')),
                                ('2', _('Wednesday')),
                                ('3', _('Thursday')),
                                ('4', _('Friday')),
                                ('5', _('Saturday')),
                                ('6', _('Sunday'))], required=True)
    time_start = fields.Float(string='Start')
    time_stop = fields.Float(string='Stop')
    availability_24 = fields.Boolean(string="All day")

    @api.onchange('availability_24')
    def onchange_availability_24(self):
        """ fill time_start et time_stop if availability_24 is True """
        for line in self:
            if line.availability_24:
                line.update({'time_start': 0.0, 'time_stop': 23.98})

    @api.onchange('time_start')
    def onchange_time_start(self):
        """ Propose automatically stop hour after start hour had been filled """
        for line in self:
            if line.time_start and not line.time_stop:
                line.time_stop = line.time_start + 1

    @api.constrains('availability_24')
    def check_availability24(self):
        """ Checks hour consistency against availability 24 """
        for line in self:
            if line.availability_24:
                line.write({'time_start': 0.0, 'time_stop': 23.98})

    @api.constrains('time_start', 'time_stop')
    def _check_time_consistency(self):
        """ Checks time consistency """
        for line in self:
            if line.time_stop <= line.time_start:
                raise ValidationError(_('End time should be after than start time'))

    @api.constrains('time_start', 'time_stop')
    def _check_time_all_day(self):
        """ Checks time all day availability """
        for timetable in self:
            if timetable.time_stop > 23.98 and timetable.time_start == 0:
                timetable.write({'availability_24': True})
