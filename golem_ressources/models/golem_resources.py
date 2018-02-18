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



from odoo import models, fields, api, _, exceptions

#Wizard pour recuperer le motif du refus d'une réservation et le stocker sur la reservation
class myWizard(models.TransientModel):
    """GOLEM Resource wizard"""
    _name = "golem.reourceswizard"

    # recuperer la reservation courant
    def _default_reservation(self):
        return self.env['golem.reservation'].browse(self._context.get('active_id'))

    rejection_reason = fields.Text()

    #override la methode d'ecriture de wizard pour stocker le motif du refus sur la reservation
    @api.model
    def create(self, vals):
        #récuperation de la reservation actuelle
        record = self.env['golem.reservation'].browse(self._context.get('active_id'))
        #stockage du motif sur la reservation
        record.rejection_reason = vals['rejection_reason']
        new_record = super(myWizard, self).create(vals)
        return new_record

#modèle de base : ressources
class GolemResources(models.Model):
    """ GOLEM Resources """
    _name = 'golem.resources'
    _description = 'GOLEM Resources'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    validation_required = fields.Boolean(default=True)
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
    user = fields.Many2one('res.users', required=True,  default=lambda self: self.env.user)
    on_behalf_of = fields.Many2one('res.partner', required=True, default=lambda self: self.env['res.partner'])
    rejection_reason = fields.Text()
    status = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('canceled', "Canceled"),
        ('validated', "Validated"),
        ('rejected', "Rejected"),
    ], default='draft')

    @api.multi
    def status_draft(self):
        self.status = 'draft'

    @api.multi
    def status_confirm(self):
        self.status = 'confirmed'
        if( not self.linked_resource.validation_required) :
            self.status='validated'


    @api.multi
    def status_canceled(self):
        self.status = 'canceled'

    @api.multi
    def status_validated(self):
        self.status = 'validated'


    @api.multi
    def status_rejected(self):
        self.status = 'rejected'
        #lancement du wizard une fois l'administrateur rejet une reservation
        return {
                'name'      : _('Please enter the reseaon of rejection'),
                'type'      : 'ir.actions.act_window',
                'res_model' : 'golem.reourceswizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
            }


    @api.constrains('status')
    def _onConfirmReservation(self):
        if self.status == 'confirmed':
            #verifyin is the reservation is taking place out of the resource availibility period
            if(self.start_date < self.linked_resource.start_of_availability_date or self.end_date > self.linked_resource.end_of_availability_date ):
                raise exceptions.UserError('Not allowed, the resource is not available in this period, please choose another périod before confirming %s' % self.linked_resource.start_of_availability_date)
            else :
                #verifying if the reservation is taking place out the availibility timetable
                #defining a boolean flag, which will determine if the day of the reservation is available
                r_allowed = False
                for day in self.linked_resource.timetable :
                    #if the day is available, look for the time if it's inside the resource timetable availibility
                    if day.name.id_day == fields.Datetime.from_string(self.start_date).weekday():
                        start_hour = fields.Datetime.from_string(self.start_date).hour
                        start_min = float(fields.Datetime.from_string(self.start_date).minute) #+(int(fields.Datetime.from_string(self.start_date).min))/100
                        start_time_r = start_hour + start_min/100
                        start_hour = fields.Datetime.from_string(self.end_date).hour
                        start_min = float(fields.Datetime.from_string(self.end_date).minute) #+(int(fields.Datetime.from_string(self.start_date).min))/100
                        end_time_r = start_hour + start_min/100
                        #if the time is suitable, the flag state is changed
                        if(start_time_r > day.start_time and end_time_r < day.end_time):
                            r_allowed = True
                #if the flag is changed no erreur is raised.
                if(not r_allowed):
                            raise exceptions.UserError("Not allowed, the resource is not available during this timetable, please choose another time before confirming ")
                #verifying if the resource is already taken during this period
                for reservation in self.linked_resource.reservation :
                    if(self.id != reservation.id and reservation.status == 'confirmed' and not (self.end_date < reservation.start_date or self.start_date > reservation.end_date)):
                        raise exceptions.UserError("Not allowed, the resource is taken during this period, please choose another période before confirming ")
                    elif (not self.linked_resource.validation_required):
                        self.status = 'validated'



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
    id_day = fields.Integer()

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
