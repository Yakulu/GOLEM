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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'


    #ajout d'un champs O2M vers activity_id de golem.activity.queue
    activity_queue_ids = fields.One2many('golem.activity.queue',
                        'activity_id','Pending registration')
    # un booleen pour determiner si une fille d'attente est autorisé
    queue_allowed = fields.Boolean(default=True)
    # un booleen pour automatisé l'inscription sur une activité depuis la file d'attente
    automated_registration_from_queue = fields.Boolean(default=True)
    #ajout d'un champs pour calculer le nombre d'inscription en file d'attente
    queue_activity_number = fields.Integer(compute="_queue_activity_number",
                                           store=True, string='Pending registration number')

    #mettre à jour le status d'activité remplis sur chaque attente
    @api.constrains('places_remain')
    def updateActivityState(self):
        """updates queue.is_activity_full based on places_remain"""
        for activity in self:
            for queue in self.activity_queue_ids:
                if activity.places_remain == 0:
                    queue.is_activity_full = "Full activity"
                else:
                    queue.is_activity_full = "Not full activity"
    #Ajouter/supprimer une file à l'activité et afficher popup pour traitement automatisé
    @api.multi
    def queue_allowed_toggle(self):
        for activity in self:
            if activity.queue_allowed:
                activity.queue_allowed = not activity.queue_allowed
                activity.automated_registration_from_queue = False
            else:
                activity.queue_allowed = not activity.queue_allowed



    #contraint sur nombre d'inscription : une desincription declanche une inscription depuis attente
    @api.multi
    @api.constrains('activity_registration_ids')
    def _automatedRegistrationFromQueue(self):
        for record in self:
            # 1 verifier si une place est disponible sur activité
            #2 verifier si la file contient des element
            #3 verifier si la file est activé
            #4 verifier si linscription automatique depuis la file est activé
            if (len(record.activity_registration_ids) < record.places and
                record.queue_activity_number > 0 and
                record.queue_allowed and
                record.automated_registration_from_queue):
                #recupérer la liste en file d'attente
                queues = record.activity_queue_ids
                #trier la liste selon l'id : récupérer l'ancien element
                queues_sorted = sorted(queues, key=lambda k: k['id'])
                #suppose que le membre est enrigistré
                membre_registred = True
                #parcourir les element sur l'attente
                for queue in queues_sorted:
                    #inverse l'etat du memebre
                    membre_registred = False
                    #recuperer la liste des registration
                    registrations = record.activity_registration_ids
                    #parcourir les registration afin de vérifier si le memebre sur l'attente déja inscrit
                    for registration in registrations:
                        #compare le membre sur l'attente au membre sur l'inscription
                        if queue.member_id == registration.member_id:
                            #si membre trouvé on mentionne enregistré, on passe au registration suivante
                            membre_registred = True
                            break
                    #à la sortie de la boucle si le membre nest pas sur inscription faire une
                    if not membre_registred:
                        #valeures pour creer une inscritpion apartir de la file
                        values = {
                            'activity_id' : queue.activity_id,
                            'member_id' : queue.member_id
                            }
                        # creation d'inscription
                        record.activity_registration_ids = [(0, 0,values)]
                        #suppression de l'element de la file d'attente
                        record.activity_queue_ids = [(2, queue.id, 0)]
                        #sortir de la boucle parcourissante la queue puisque inscription faite
                        break



    #calculer le nombre d'inscription sur la file d'attente
    @api.multi
    @api.depends('activity_queue_ids')
    def _queue_activity_number(self):
        for activity in self:
            activity.queue_activity_number = len(activity.activity_queue_ids)

    #lancer une fenetre pour inscritpion en file d'attente à partir du boutton
    @api.multi
    def queue_register(self):
        self.ensure_one()
        activity_id = self[0]
        return {
            'name'      : _('Register in the queue'),
            'type'      : 'ir.actions.act_window',
            'res_model' : 'golem.activity.queue',
            'context' :{'default_activity_id' : activity_id.id},
            'domain' : [('activity_id', '=', activity_id.id)],# activity_id.name)],#"('activity_id', '=', True)"
            'view_mode': 'tree',
            'flags': {'action_buttons': True},
            'target': 'new',
        }

    #fonction enregistrement du premier element de la liste d'ttente en inscription : mode manuel
    @api.multi
    def register_from_queue(self):
        for record in self:
            #recupérer la liste en file d'attente
            queues = record.activity_queue_ids
            #trier la liste selon l'id : récupérer l'ancien element
            queues_sorted = sorted(queues, key=lambda k: k['id'])
            #suppose que le membre est enrigistré
            membre_registred = True
            #parcourir les element sur l'attente
            for queue in queues_sorted:
                #inverse l'etat du memebre
                membre_registred = False
                #recuperer la liste des registration
                registrations = record.activity_registration_ids
                #parcourir les registration afin de vérifier si le memebre sur l'attente déja inscrit
                for registration in registrations:
                    #compare le membre sur l'attente au membre sur l'inscription
                    if queue.member_id == registration.member_id:
                        #si membre trouvé on mentionne enregistré, on passe au registration suivante
                        membre_registred = True
                        break
                #à la sortie de la boucle si le membre nest pas sur inscription faire une
                if not membre_registred:
                    #valeures pour creer une inscritpion apartir de la file
                    values = {
                        'activity_id' : queue.activity_id,
                        'member_id' : queue.member_id
                        }
                    # creation d'inscription
                    record.activity_registration_ids = [(0, 0,values)]
                    #suppression de l'element de la file d'attente
                    record.activity_queue_ids = [(2, queue.id, 0)]
                    #sortir de la boucle parcourissante la queue puisque inscription faite
                    break
            #si member_registred est true donc soit membre déja inscrit ou aucun membre sur queue
            if membre_registred:
                message = _('there is no member to register for this activity'
                            ' from queue.')
                raise ValidationError(message)
    # 1 verifie si ajout insctiption donc nombre d'inscription depasse place donc proposer queue
    #2 verifier si desincription donc place disponible pour queue(automatique ou manuel)
    @api.multi
    @api.onchange('activity_registration_ids')
    def _checkRegistrationNumber(self):
        current_activity = self._origin
        for record in self:
            #warning au cas ou le nombre d'inscription depasse le nombre de place
            if (len(record.activity_registration_ids) > record.places and
                record.queue_allowed):
                message = _('No remaining place for the activity : {}, please'
                            ' discard changes and register in the queue using'
                            ' the button bellow')
                return {
                    'warning' : {
                        'title' : _('Warning'),
                        'message': message.format(record.name),
                    }
                }
            elif (len(record.activity_registration_ids) < len(current_activity.activity_registration_ids) and
                  len(current_activity.activity_registration_ids) == record.places and
                  record.queue_activity_number > 0 ):
                #si le mode d'inscription depuis attente est activé
                if record.automated_registration_from_queue:
                    #lancer un warning informant que l'inscription automatique aura lieu apres sauvegarde
                    print("________________________testuii____________________________________")
                    warningMessage = _('There is a free place for the activity'
                                       ' : {}, once you save it will be filled'
                                       ' by the first membre from queue')
                    return {
                        'warning' : {
                            'title' : _('Warning'),
                            'message': warningMessage.format(record.name)
                            }
                        }

                #traitement manuel pour le passage de la file d'attente en inscription : button sur queue
                else :
                    warningMessage = _('There is a free place for the activity'
                                       ' : {}, you can fill it from the queue'
                                       ' using the button on queue tab')
                    return {
                        'warning' : {
                            'title' : _('Warning'),
                            'message': warningMessage.format(record.name)
                            }
                        }
