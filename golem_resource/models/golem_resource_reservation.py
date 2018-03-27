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

""" GOLEM Resource Reservation """

from math import modf
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourceReservation(models.Model):
    """ GOLEM Resource Reservation Model """
    _name = 'golem.resource.reservation'
    _description = 'GOLEM Reservation Model'
    _inherit = 'mail.thread'
    _order = 'day_start desc, hour_start asc'

    name = fields.Char(compute='_compute_name', store=True)
    # TODO: handle multiple days reservation
    date_start = fields.Datetime('Start date', required=True,
                                 index=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    date_stop = fields.Datetime('Stop date', required=True,
                                index=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    day_start = fields.Date(compute='_compute_day_hour_start', store=True)
    hour_start = fields.Float(compute='_compute_day_hour_start', store=True)
    resource_id = fields.Many2one('golem.resource', required=True, index=True,
                                  string='Resource', readonly=True,
                                  track_visibility='onchange',
                                  states={'draft': [('readonly', False)]})
    resource_avaibility_start = fields.Date(related='resource_id.avaibility_start')
    resource_avaibility_stop = fields.Date(related='resource_id.avaibility_stop')
    resource_avaibility_24_7 = fields.Boolean(related='resource_id.availibility_24_7')
    resource_timetable_ids = fields.One2many(related='resource_id.timetable_ids')

    note = fields.Text(help='Notes, optional subject for the reservation, reason')

    user_id = fields.Many2one('res.users', required=True, index=True, readonly=True,
                              string='User', default=lambda self: self.env.user,
                              states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='On behalf of',
                                 required=True, index=True, readonly=True,
                                 track_visibility='onchange',
                                 states={'draft': [('readonly', False)]})
    state = fields.Selection([('canceled', 'Canceled'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('validated', 'Validated'),
                              ('rejected', 'Rejected')],
                             default='draft', track_visibility='onchange')

    rejection_reason = fields.Text(readonly=True, track_visibility='onchange')

    @api.depends('resource_id', 'date_start')
    def _compute_name(self):
        """ Computes reservation name """
        for reservation in self:
            reservation.name = u'{}/{}'.format(reservation.resource_id.name,
                                               reservation.date_start)

    @api.depends('date_start')
    def _compute_day_hour_start(self):
        """ Computes Day and Hour Start : for better sorting """
        for reservation in self:
            if reservation.date_start:
                date_start = fields.Datetime.from_string(reservation.date_start)
                reservation.day_start = date_start.date().isoformat()
                reservation.hour_start = date_start.hour + date_start.minute / 60.0

    @api.onchange('date_start')
    def onchange_date_start(self):
        """ Propose automatically stop hour after start hour had been filled """
        for reservation in self:
            if reservation.date_start:
                start = fields.Datetime.from_string(reservation.date_start)
                duration = timedelta(hours=1)
                reservation.date_stop = start + duration


    @api.constrains('date_start', 'date_stop')
    def _check_date_consistency(self):
        """ Checks date consistency """
        for reservation in self:
            if reservation.date_stop <= reservation.date_start:
                raise ValidationError(_('Stop date should be after start date'))

    @api.multi
    def state_draft(self):
        """ Status to draft """
        self.write({'state': 'draft'})

    @api.multi
    def state_confirm(self):
        """ Confirms reservation, or validates it if not workflow is involved """
        for reservation in self:
            # Needed, for constraint checking
            reservation.state = 'confirmed'
            if not reservation.resource_id.validation_required:
                reservation.state = 'validated'


    @api.multi
    def state_canceled(self):
        """ Status to cancel """
        self.write({'state': 'canceled'})

    @api.multi
    def state_validated(self):
        """ Status to validated """
        self.write({'state': 'validated'})

    @api.multi
    def state_rejected(self):
        """ Wizard call for reservation reject """
        self.ensure_one()
        reservation_id = self[0]
        return {'name' : _('Please enter the rejection reason'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'golem.reservation.rejection.wizard',
                'context': {'default_reservation_id': reservation_id.id},
                'view_mode': 'form',
                'target': 'new'}


    @api.constrains('state')
    def check_access(self):
        """ Checks access when state is updated """
        reservation = self[0]
        if reservation.state in ('rejected', 'validated'):
            if not self.env.user.has_group('golem_base.group_golem_manager'):
                verr = _('You do not have permissions to validate or reject a reservation.')
                raise ValidationError(verr)

    @api.constrains('state')
    def check_confirmed(self):
        """ Check date coherence on reservation confirmation """
        for reservation in self:
            if reservation.state == 'confirmed':
                # Check is reservation is not taking place out of the resource avaibility period
                if reservation.date_start < reservation.resource_id.avaibility_start or \
                   reservation.date_stop > reservation.resource_id.avaibility_stop:
                    verr = _('Not allowed, the resource is not available in '
                             'this period, please choose another périod before '
                             'confirming')
                    raise ValidationError(verr)
                #check if the resource hasn't a total availibility
                if not reservation.resource_id.availibility_24_7:
                    # Check if reservation is not taking place out the avaibility timetables
                    date_start = fields.Datetime.from_string(reservation.date_start)
                    date_stop = fields.Datetime.from_string(reservation.date_stop)
                    reservation_period = [date_start + timedelta(days=x) for x in range(
                        (date_stop - date_start).days + 1)]
                    for reservation_day in reservation_period:
                        is_day_allowed = False
                        for timetable in reservation.resource_id.timetable_ids:
                            # Check for the time according to resource timetable avaibility
                            #date = fields.Datetime.from_string(reservation_day)
                            if int(timetable.weekday) == reservation_day.weekday():
                                is_day_allowed = True
                                #only check if the day hasn't a 24 availibility
                                if not timetable.availibility_24:
                                    reservation_day_date = reservation_day.date()
                                    day_start = date_start.date()
                                    day_stop = date_stop.date()
                                    if reservation_day_date == day_start and \
                                        reservation_day_date == day_stop:
                                        hour_start = date_start.hour + date_start.minute / 60.0
                                        hour_stop = date_stop.hour + date_stop.minute / 60.0
                                    elif reservation_day_date == day_start:
                                        hour_start = date_start.hour + date_start.minute / 60.0
                                        hour_stop = 23.98 # Just before 23:59
                                    elif reservation_day_date == day_stop:
                                        hour_start = 0.0
                                        hour_stop = date_stop.hour + date_stop.minute / 60.0
                                    else:
                                        #if the day is not a start nor stop it
                                        #should be covered on all day
                                        #strange, as availibility_24 is not True
                                        hour_start = 0.0
                                        hour_stop = 23.98

                                    if is_day_allowed and (hour_start < timetable.time_start or \
                                        hour_stop > timetable.time_stop):
                                        verr = _('Not allowed, the resource is not available '
                                                 'during this period, please choose another '
                                                 'time before confirming.')
                                        raise ValidationError(verr)
                        if not is_day_allowed:
                            verr = _('Not allowed, the resource is not available '
                                     'this day : {}. Please choose another '
                                     'date.'.format(reservation_day.strftime('%A')))
                            raise ValidationError(verr)
                # Check if the resource is already taken during this period
                # PERF : check for res that can be in conflict,
                # do not iterate over all reservations
                domain = [('resource_id', '=', reservation.resource_id.id),
                          ('date_start', '<=', reservation.date_stop),
                          ('date_stop', '>=', reservation.date_start),
                          ('state', 'in', ('confirmed', 'validated')),
                          ('id', '!=', reservation.id)]
                reservations = self.env['golem.resource.reservation'].search(domain)
                for other_res in reservations:
                    if (other_res.date_start < reservation.date_start < other_res.date_stop) or \
                       (other_res.date_start < reservation.date_stop < other_res.date_stop):
                        verr = _('Not allowed, the resource is already taken '
                                 'during this period : from {} to {} this day, '
                                 'please choose another périod before confirming.')
                        raise ValidationError(verr.format(other_res.date_start,
                                                          other_res.date_stop))
