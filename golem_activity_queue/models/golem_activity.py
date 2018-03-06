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

""" GOLEM Activity adaptations """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'

    #ajout d'un champs O2M vers activity_id de golem.activity.queue
    activity_queue_ids = fields.One2many('golem.activity.queue',
                                         'activity_id', 'Pending registration')
    # un booleen pour determiner si une fille d'attente est autorisé
    queue_allowed = fields.Boolean(default=True, readonly=True)
    # un booleen pour automatisé l'inscription sur une activité depuis la file d'attente
    auto_registration_from_queue = fields.Boolean(default=True, readonly=True)
    #ajout d'un champs pour calculer le nombre d'inscription en file d'attente
    queue_activity_number = fields.Integer(compute="_compute_queue_activity_number",
                                           store=True, string='Pending registration number')
    #changer le mode de basculement en cas de desinctiption
    @api.multi
    def auto_registration_toggle(self):
        """ switch registration from queueu mode """
        for activity in self:
            activity.auto_registration_from_queue = not activity.auto_registration_from_queue

    #supprimer les personnes en attente si une inscription directement est faite
    @api.multi
    def write(self, vals):
        """ Override method write to delete record from queue if they register in activity"""
        super(GolemActivity, self).write(vals)
        #recupérer les modification au niveau des registrations
        registrations = vals.get('activity_registration_ids')
        if registrations:
            #parcourir les registrations
            for registration in registrations:
                #s'il une nouvelle registration est trouvé
                if registration[0] == 0:
                    #recupérer les données de la registration
                    act_id = registration[2].get('activity_id')
                    mem_id = registration[2].get('member_id')
                    domain = [('activity_id', '=', act_id),
                              ('member_id', '=', mem_id)]
                    #chercher si le meme nomre est inscrit sur lattente du meme activité
                    queue = self.env['golem.activity.queue'].search(domain)
                    if queue:
                        #supprimer l'inscription sur la queue
                        self.activity_queue_ids = [(2, queue.id, 0)]
        return True

    #Ajouter/supprimer une file à l'activité et afficher popup pour traitement automatisé
    @api.multi
    def queue_allowed_toggle(self):
        """ Toggle queue_alowed boolean """
        for activity in self:
            #si l'activité contient une file
            if activity.queue_allowed:
                # si la queue déja contient des elements à supprimer
                if len(activity.activity_queue_ids) > 0:
                    #parcourir et supprimer les element de la queue
                    for queue in activity.activity_queue_ids:
                        activity.activity_queue_ids = [(2, queue.id, 0)]
                #changer l'état de queue allowed et automated_registration en false
                activity.queue_allowed = False
                activity.auto_registration_from_queue = False

            else:
                #lancer popup pour choisir activité à s'inscrire
                self.ensure_one()
                activity_id = self[0]

                return {
                    'name'      : _('Choose the activity to register in'),
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'golem.activity.automated.queue.activate.wizard',
                    'view_mode': 'form',
                    'context' : {'default_activity_id' : activity_id.id},
                    'target': 'new',
                }



    #contraint sur nombre d'inscription : une desincription declanche une inscription
    #depuis attente mode automatique
    @api.multi
    @api.constrains('activity_registration_ids')
    def _auto_registration_from_queue(self):
        """automated registration from queue"""
        for record in self:
            # 1 verifier si une place est disponible sur activité
            #2 verifier si la file contient des element
            #3 verifier si la file est activé
            #4 verifier si linscription automatique depuis la file est activé
            if (len(record.activity_registration_ids) < record.places and
                    record.queue_activity_number > 0 and
                    record.queue_allowed and
                    record.auto_registration_from_queue):
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
                    #parcourir les registration afin de vérifier si le memebre sur l'attente
                    #déja inscrit
                    for registration in registrations:
                        #compare le membre sur l'attente au membre sur l'inscription
                        if queue.member_id == registration.member_id:
                            #si membre trouvé inscrit sur l'activité on le supprime de la queue
                            record.activity_queue_ids = [(2, queue.id, 0)]
                            #si membre trouvé on mentionne enregistré, on passe au
                            #registration suivante
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
                        record.activity_registration_ids = [(0, 0, values)]
                        #suppression de l'element de la file d'attente
                        record.activity_queue_ids = [(2, queue.id, 0)]
                        #sortir de la boucle parcourissante la queue puisque inscription faite
                        break



    #calculer le nombre d'inscription sur la file d'attente
    @api.multi
    @api.depends('activity_queue_ids')
    def _compute_queue_activity_number(self):
        """ compute number of queue registration for activity"""
        for activity in self:
            activity.queue_activity_number = len(activity.activity_queue_ids)

    #lancer une fenetre pour inscritpion en file d'attente à partir du boutton
    @api.multi
    def queue_register(self):
        """ launch a wizard to register in queue """
        self.ensure_one()
        activity_id = self[0]
        return {
            'name'      : _('Register in the queue'),
            'type'      : 'ir.actions.act_window',
            'res_model' : 'golem.activity.queue',
            'context' :{'default_activity_id' : activity_id.id},
            'domain' : [('activity_id', '=', activity_id.id)],
            'view_mode': 'tree',
            'flags': {'action_buttons': True},
            'target': 'new',
        }

    #fonction enregistrement du premier element de la liste d'ttente en inscription : mode manuel
    @api.multi
    def register_from_queue(self):
        """ register member from queue"""
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
                #parcourir les registration afin de vérifier si le memebre sur
                #l'attente déja inscrit
                for registration in registrations:
                    #compare le membre sur l'attente au membre sur l'inscription
                    if queue.member_id == registration.member_id:
                        #si membre trouvé inscrit sur l'activité on le supprime de la queue
                        record.activity_queue_ids = [(2, queue.id, 0)]
                        # on mentionne enregistré, on passe au registration suivante
                        membre_registred = True
                        #on sort de la boucle de registration et on passe à
                        #l'element suivant de l'attente
                        break
                #à la sortie de la boucle si le membre nest pas sur inscription faire une
                if not membre_registred:
                    #valeures pour creer une inscritpion apartir de la file
                    values = {
                        'activity_id' : queue.activity_id,
                        'member_id' : queue.member_id
                        }
                    # creation d'inscription
                    record.activity_registration_ids = [(0, 0, values)]
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
    def _check_registration_number(self):
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
                  record.queue_activity_number > 0):
                #si le mode d'inscription depuis attente est activé
                if record.auto_registration_from_queue:
                    #lancer un warning informant que l'inscription automatique aura
                    #lieu apres sauvegarde
                    warning_message = _('There is a free place for the activity'
                                        ' : {}, once you save it will be filled'
                                        ' by the first membre from queue')
                    return {
                        'warning' : {
                            'title' : _('Warning'),
                            'message': warning_message.format(record.name)
                            }
                        }

                #traitement manuel pour le passage de la file d'attente en inscription
                # : button sur queue
                else:
                    warning_message = _('There is a free place for the activity'
                                        ' : {}, you can fill it from the queue'
                                        ' using the button on queue tab')
                    return {
                        'warning' : {
                            'title' : _('Warning'),
                            'message': warning_message.format(record.name)
                            }
                        }
