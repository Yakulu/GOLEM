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



from odoo import models, fields, api

class GolemResources(models.Model):
    """ GOLEM Resources """
    _name = 'golem.resources'
    _description = 'GOLEM Resources'

    name = fields.Char()
    resource_type = fields.Many2one("golem.resourcetype", string="Resource type")
    resource_responsible = fields.Many2one("res.partner", string="Resource Responsible")
    article_link = fields.Many2one("product.template", string="Article Link")
    #Configuration de disponibilité
    start_of_availability_date = fields.Date(string="Start of availibility date ")
    end_of_availability_date = fields.Date(string="End of availibility date ")
    weekdays_of_availibility = fields.Many2many('golem.weekday', string="Weekdays of availibility")


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

class GolemResourceType(models.Model):
    """ GOLEM Resource Type """
    _name = 'golem.resourcetype'
    _description = 'GOLEM Resource Type'

    name = fields.Char(string='Resource Type')

class GolemWeekDays(models.Model):
    """ GOLEM Week Days """
    _name = 'golem.weekday'
    _description = 'GOLEM Week Day'

    name = fields.Char(string='Week Day')
