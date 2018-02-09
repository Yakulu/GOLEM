# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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



from odoo import models, fields, api, _, exceptions
import logging

_logger = logging.getLogger(__name__)
#modèle de base : ressources
class GolemResources(models.Model):
    """ GOLEM Resources """
    _name = 'golem.resources'
    _description = 'GOLEM Resources'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    resource_type = fields.Many2one("golem.resourcetype")
    resource_responsible = fields.Many2one("res.partner")
    article_link = fields.Many2one("product.template")

    #Configuration de disponibilité(période, jours et horaire)
    start_of_availability_date = fields.Date(required=True)
    end_of_availability_date = fields.Date(required=True)
    timetable = fields.One2many("golem.timetable", "resource_id", string="Availibility timetable")
    reservation = fields.One2many("golem.reservation", "linked_resource")

    @api.multi
    def active_change(self):
        self.active = not self.active



#modèle gestion des reservation
class GolemReservation(models.Model):
    """ GOLEM Reservation """
    _name = 'golem.reservation'
    _description = 'GOLEM Reservation'

    start_date = fields.Datetime()
    end_date = fields.Datetime()
    linked_resource = fields.Many2one('golem.resources', required=True)
    user = fields.Many2one('res.users', required=True)
    on_behalf_of = fields.Many2one('res.partner', required=True)
    #statut=fields.Char()
    status = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('canceled', "Canceled"),
    ], default='draft')

    @api.multi
    def status_draft(self):
        self.status = 'draft'

    @api.multi
    def status_confirm(self):
        self.status = 'confirmed'


    @api.multi
    def status_canceled(self):
        self.status = 'canceled'

    @api.constrains('status')
    def _onConfirmReservation(self):
        if self.status == 'confirmed':
            if(self.start_date < self.linked_resource.start_of_availability_date or self.end_date > self.linked_resource.end_of_availability_date ):
                raise exceptions.UserError('Not allowed, the resource is not available in this period, please choose another périod before confirming %s' % self.linked_resource.start_of_availability_date)
            else :
                for reservation in self.linked_resource.reservation :
                    if(self.id != reservation.id and reservation.status == 'confirmed' and not (self.end_date < reservation.start_date or self.start_date > reservation.end_date)):
                        raise exceptions.UserError("Not allowed, the resource is taken during this period, please choose another période before confirming ")



#modèle de base pour identifier le type de la ressource
class GolemResourceType(models.Model):
    """ GOLEM Resource Type """
    _name = 'golem.resourcetype'
    _description = 'GOLEM Resource Type'

    name = fields.Char(string='Resource Type',required=True)

#modèle de base pour stocker les jours de la semaine
class GolemWeekDay(models.Model):
    """ GOLEM Week Day """
    _name = 'golem.weekday'
    _description = 'GOLEM Week Day'

    name = fields.Char(string='Week Day')

#modèle de gestion horaire
class GolemTimetable(models.Model):
    """ Golem Timetable """
    _name = "golem.timetable"
    _description = "Golem Timetable"

    resource_id = fields.Many2one("golem.resources", required=True)
    name = fields.Many2one("golem.weekday", required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)

    @api.constrains('start_time', 'end_time')
    def _check_time_consistency(self):
        if self.end_time < self.start_time:
            raise exceptions.ValidationError(_('End time should be higher than start time'))
