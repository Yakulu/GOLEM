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

from math import modf
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GolemResource(models.Model):
    """ GOLEM Resource Model """
    _name = 'golem.resource'
    _description = 'GOLEM Resource Model'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    validation_required = fields.Boolean(default=True,
                                         string='Is validation required ?')
    type_id = fields.Many2one('golem.resource.type',
                              index=True, string='Resource Type')
    supervisor_id = fields.Many2one('res.partner', index=True, string='Supervisor')
    product_tmpl_id = fields.Many2one('product.template', index=True,
                                      string='Linked product')

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


class GolemResourceReservation(models.Model):
    """ GOLEM Resource Reservation Model """
    _name = 'golem.resource.reservation'
    _description = 'GOLEM Reservation Model'

    name = fields.Char(compute='_compute_name', store=True)
    # TODO: handle multiple days reservation
    date = fields.Date(required=True, index=True)
    hour_start = fields.Float('Start hour', required=True)
    hour_stop = fields.Float('Stop hour', required=True)
    date_start = fields.Datetime(compute='_compute_date_start', store=True, index=True)
    date_stop = fields.Datetime(compute='_compute_date_stop', store=True, index=True)

    resource_id = fields.Many2one('golem.resource', required=True, index=True,
                                  string='Resource')
    user_id = fields.Many2one('res.users', required=True, index=True,
                              string='User',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='On behalf of',
                                 required=True, index=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
    ], default='draft')

    rejection_reason = fields.Text()

    @api.depends('resource_id', 'date')
    def _compute_name(self):
        """ Computes reservation name """
        for reservation in self:
            reservation.name = u'{}/{}'.format(reservation.resource_id.name,
                                               reservation.date)

    @api.depends('date', 'hour_start')
    def _compute_date_start(self):
        """ Computes Date start """
        for reservation in self:
            hour_start, minute_start = modf(reservation.hour_start)
            minute_start = int(round(minute_start * 60))
            reservation.date_start = u'{} {}:{}'.format(reservation.date,
                                                        hour_start, minute_start)

    @api.depends('date', 'hour_stop')
    def _compute_date_stop(self):
        """ Computes Date stop """
        for reservation in self:
            hour_stop, minute_stop = modf(reservation.hour_stop)
            minute_stop = int(round(minute_stop * 60))
            reservation.date_stop = u'{} {}:{}'.format(reservation.date,
                                                       hour_stop, minute_stop)

    @api.multi
    def status_draft(self):
        """ Status to draft """
        self.write({'status': 'draft'})

    @api.multi
    def status_confirm(self):
        """ Confirms reservation, or validates it if not workflow is involved """
        for reservation in self:
            if reservation.resource_id.validation_required:
                reservation.status = 'confirmed'
            else:
                reservation.status_validated()


    @api.multi
    def status_canceled(self):
        """ Status to cancel """
        self.write({'status': 'canceled'})

    @api.multi
    def status_validated(self):
        """ Status to validated """
        self.write({'status': 'validated'})

    @api.multi
    def status_rejected(self):
        """ Wizard call for reservation reject """
        self.ensure_one()
        reservation_id = self[0]
        return {'name' : _('Please enter the rejection reason'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'golem.reservation.rejection.wizard',
                'context': {'default_reservation_id': reservation_id.id},
                'view_mode': 'form',
                'target': 'new'}


    @api.constrains('status')
    def check_confirmed(self):
        """ Check date coherence on reservation confirmation """
        for reservation in self:
            if reservation.status == 'confirmed':
                # Check is reservation is not taking place out of the resource avaibility period
                if reservation.date < reservation.resource_id.avaibility_start or \
                   reservation.date > reservation.resource_id.avaibility_stop:
                    uerr = _('Not allowed, the resource is not available in '
                             'this period, please choose another périod before '
                             'confirming')
                    raise UserError(uerr)
                # Check if reservation is not taking place out the avaibility timetables
                is_day_allowed = False
                for timetable in reservation.resource_id.timetable_ids:
                    # Check for the time according to resource timetable avaibility
                    date = fields.Datetime.from_string(reservation.date)
                    if int(timetable.weekday) == date.weekday():
                        is_day_allowed = True
                        if reservation.hour_start < timetable.date_start or \
                            reservation.hour_stop > timetable.date_stop:
                            uerr = _('Not allowed, the resource is not available '
                                     'during this period, please choose another '
                                     'time before confirming.')
                            raise UserError(uerr)
                if not is_day_allowed:
                    uerr = _('Not allowed, the resource is not available '
                             'this day. Please choose another date.')
                    raise UserError(uerr)
                # Check if the resource is already taken during this period
                # PERF : check the date, not iterate over all reservations
                domain = [('resource_id', '=', reservation.resource_id.id),
                          ('date', '=', reservation.date),
                          ('status', '=', 'confirmed'),
                          ('id', '!=', reservation.id)]
                reservations = self.env['golem.resource.reservation'].search(domain)
                for other_res in reservations:
                    if (other_res.hour_start < reservation.hour_start < other_res.hour_stop) or \
                        (other_res.hour_start < reservation.hour_stop < other_res.hour_stop):
                        uerr = _('Not allowed, the resource is already taken '
                                 'during this period : from {} to {} this day, '
                                 'please choose another périod before confirming.')
                        raise UserError(uerr.format(reservation.date_start,
                                                    reservation.date_stop))
                # Finally, validate the reservation if all checks have passed
                if reservation.resource_id.validation_required:
                    reservation.status = 'validated'


class GolemResourceType(models.Model):
    """ GOLEM Resource Type """
    _name = 'golem.resource.type'
    _description = 'GOLEM Resource Type'
    _sql_constraints = [('golem_resource_type_name_uniq',
                         'UNIQUE (name)',
                         'Resource type must be unique.')]

    name = fields.Char(string='Resource Type', required=True, index=True)

class GolemTimetable(models.Model):
    """ Golem Timetable """
    _name = "golem.resource.timetable"
    _description = "Golem Timetable"
    _rec_name = 'weekday'

    resource_id = fields.Many2one('golem.resource', required=True,
                                  string='Linked resource')
    weekday = fields.Selection([('0', _('Monday')),
                                ('1', _('Tuesday')),
                                ('2', _('Wednesday')),
                                ('3', _('Thursday')),
                                ('4', _('Friday')),
                                ('5', _('Saturday')),
                                ('6', _('Sunday'))], copy=False)
    time_start = fields.Float(required=True, string='Start')
    time_stop = fields.Float(required=True, string='Stop')

    @api.constrains('time_start', 'time_stop')
    def _check_time_consistency(self):
        for timetable in self:
            if timetable.time_stop < timetable.time_start:
                raise ValidationError(_('End time should be after than start time'))
