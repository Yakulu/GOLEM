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
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GolemResourceReservation(models.Model):
    """ GOLEM Resource Reservation Model """
    _name = 'golem.resource.reservation'
    _description = 'GOLEM Reservation Model'
    _inherit = 'mail.thread'
    _order = 'date desc,hour_start asc'

    name = fields.Char(compute='_compute_name', store=True)
    # TODO: handle multiple days reservation
    date = fields.Date(required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    hour_start = fields.Float('Start hour', required=True, readonly=True,
                              states={'draft': [('readonly', False)]})
    hour_stop = fields.Float('Stop hour', required=True, readonly=True,
                             states={'draft': [('readonly', False)]})
    date_start = fields.Datetime(compute='_compute_date_start', store=True, index=True)
    date_stop = fields.Datetime(compute='_compute_date_stop', store=True, index=True)

    resource_id = fields.Many2one('golem.resource', required=True, index=True,
                                  string='Resource', readonly=True,
                                  track_visibility='onchange',
                                  states={'draft': [('readonly', False)]})
    resource_avaibility_start = fields.Date(related='resource_id.avaibility_start')
    resource_avaibility_stop = fields.Date(related='resource_id.avaibility_stop')
    resource_timetable_ids = fields.One2many(related='resource_id.timetable_ids')

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
            minute_start, hour_start = modf(reservation.hour_start)
            hour_start = int(hour_start)
            minute_start = int(round(minute_start * 60))
            reservation.date_start = u'{} {}:{}:00'.format(reservation.date,
                                                           hour_start, minute_start)

    @api.depends('date', 'hour_stop')
    def _compute_date_stop(self):
        """ Computes Date stop """
        for reservation in self:
            minute_stop, hour_stop = modf(reservation.hour_stop)
            hour_stop = int(hour_stop)
            minute_stop = int(round(minute_stop * 60))
            reservation.date_stop = u'{} {}:{}:00'.format(reservation.date,
                                                          hour_stop, minute_stop)

    @api.onchange('hour_start')
    def onchange_hour_start(self):
        """ Propose automatically stop hour after start hour had been filled """
        for reservation in self:
            if reservation.hour_start and not reservation.hour_stop:
                reservation.hour_stop = reservation.hour_start + 1

    @api.constrains('hour_start', 'hour_stop')
    def _check_hour_consistency(self):
        """ Checks hour consistency """
        for reservation in self:
            if reservation.hour_stop < reservation.hour_start:
                raise ValidationError(_('End time should be after than start time'))

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
                uerr = _('You do not have permissions to validate or reject a reservation.')
                raise UserError(uerr)

    @api.constrains('state')
    def check_confirmed(self):
        """ Check date coherence on reservation confirmation """
        for reservation in self:
            if reservation.state == 'confirmed':
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
                        if reservation.hour_start < timetable.time_start or \
                            reservation.hour_stop > timetable.time_stop:
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
                          ('state', 'in', ('confirmed', 'validated')),
                          ('id', '!=', reservation.id)]
                reservations = self.env['golem.resource.reservation'].search(domain)
                for other_res in reservations:
                    if (other_res.hour_start <= reservation.hour_start <= other_res.hour_stop) or \
                        (other_res.hour_start <= reservation.hour_stop <= other_res.hour_stop):
                        uerr = _('Not allowed, the resource is already taken '
                                 'during this period : from {} to {} this day, '
                                 'please choose another périod before confirming.')
                        raise UserError(uerr.format(other_res.date_start,
                                                    other_res.date_stop))
