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



from odoo import models, fields, api, exceptions
#modèle de base : ressources
class GolemResources(models.Model):
    """ GOLEM Resources """
    _name = 'golem.resources'
    _description = 'GOLEM Resources'

    name = fields.Char()
    active = fields.Boolean(default=False)
    resource_type = fields.Many2one("golem.resourcetype", string="Resource type")
    resource_responsible = fields.Many2one("res.partner", string="Resource Responsible")
    article_link = fields.Many2one("product.template", string="Article Link")

    #Configuration de disponibilité(période, jours et horaire)
    start_of_availability_date = fields.Date(string="Start of availibility date ")
    end_of_availability_date = fields.Date(string="End of availibility date ")
    weekdays_of_availibility = fields.Many2many('golem.weekday', string="Weekdays of availibility")
    timetable = fields.One2many("golem.timetable", "resource_id", string="Availibility timetable")

    @api.multi
    def active_change(self):
        self.active = not self.active



#modèle gestion des reservation
class GolemReservation(models.Model):
    """ GOLEM Reservation """
    _name = 'golem.reservation'
    _description = 'GOLEM Reservation'

    start_date = fields.Datetime(string='Start date')
    end_date = fields.Datetime(string='End date')
    linked_resource = fields.Many2one('golem.resources', string="Linked resource")
    user = fields.Many2one('res.users', required=True)
    on_behalf_of = fields.Many2one('res.partner', required=True)
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

#modèle de base pour identifier le type de la ressource
class GolemResourceType(models.Model):
    """ GOLEM Resource Type """
    _name = 'golem.resourcetype'
    _description = 'GOLEM Resource Type'

    name = fields.Char(string='Resource Type')

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
        for r in self:
            if r.end_time < r.start_time:
                raise exceptions.ValidationError('End time should be higher than start time')
