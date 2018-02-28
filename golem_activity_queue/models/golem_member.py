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

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    #ajout d'un champs O2M vers member_id de golem.activity.queue
    activity_queue_ids = fields.One2many('golem.activity.queue',
                                         'member_id', 'Pending registration')

    @api.multi
    def write(self, vals):
        registrations_edited = vals.get('activity_registration_ids')
        if registrations_edited:
            for registration_edited in registrations_edited:
                if registration_edited[0] == 2:
                    registration_removed = self.env['golem.activity.registration'].browse(registration_edited[1])
                    activity_removed = self.env['golem.activity'].browse(registration_removed.activity_id.id)
                    if (activity_removed.queue_allowed and
                            activity_removed.auto_registration_from_queue and
                            activity_removed.queue_activity_number > 0):
                        #récupérer  la liste des attente lié à l'activité
                        queues = activity_removed.activity_queue_ids
                        #trier la liste selon l'id : récupérer l'ancien element
                        queues_sorted = sorted(queues, key=lambda k: k['id'])
                        #suppose que le membre est enrigistré
                        membre_registred = True
                        #parcourir les element sur l'attente
                        for queue in queues_sorted:
                            #inverse l'etat du memebre
                            membre_registred = False
                            #recuperer la liste des registration
                            registrations = activity_removed.activity_registration_ids
                            #parcourir les registration afin de vérifier si le memebre sur
                            #l'attente déja inscrit
                            for registration in registrations:
                                #compare le membre sur l'attente au membre sur l'inscription
                                if queue.member_id == registration.member_id:
                                    #si membre trouvé inscrit sur l'activité on le
                                    #supprime de la queue
                                    activity_removed.activity_queue_ids = [(2, queue.id, 0)]
                                    #si membre trouvé on mentionne enregistré, on passe au
                                    #registration suivante
                                    membre_registred = True
                                    break
                            #à la sortie de la boucle si le membre nest pas sur
                            #inscription faire une
                            if not membre_registred:
                                #valeures pour creer une inscritpion apartir de la file
                                values = {
                                    'activity_id' : queue.activity_id,
                                    'member_id' : queue.member_id
                                    }

                                super(GolemMember, self).write(vals)
                                # creation d'inscription
                                activity_removed.activity_registration_ids = [(0, 0, values)]
                                #suppression de l'element de la file d'attente
                                activity_removed.activity_queue_ids = [(2, queue.id, 0)]
                                #afficher un message informatif
                                warning_message = _('There is a free place for the activity'
                                                    ' : {}, once you save it will be filled'
                                                    ' by the first membre from queue')
                                print warning_message.format(activity_removed.name)
                                #sortir de la boucle parcourissante la queue puisque
                                # inscription faite
                                break
                    elif (activity_removed.queue_allowed and
                          activity_removed.queue_activity_number > 0):
                        warning_message = _('There is a free place for the activity'
                                            ' : {}, you can fill it from the queue'
                                            ' using the button on queue tab')
                        print warning_message.format(activity_removed.name)
        return True
        
    #verifier si nombre d'inscription sur activité est supérieur au place disponible
    #inviter l'utilisateur à s'inscrire sur l'attente
    @api.multi
    @api.onchange('activity_registration_ids')
    def _check_registration_number(self):
        """ check activity registration number """
        self.ensure_one()
        member_id = self[0]
        #recupérer la liste des inscription pour le membbre courant
        for registration in member_id.activity_registration_ids:
            #recupérer l'activité liée
            activity = registration.activity_id
            #vérifier si le nombre d'inscription depasse le nombre de places sur activité
            if len(activity.activity_registration_ids) > activity.places and activity.queue_allowed:
                warning_message = _('This activity : {} is already full, please'
                                    ' discard changes and register in'
                                    ' the queue using the bellow button')
                return {
                    'warning' : {
                        'title' : _('Warning'),
                        'message': warning_message.format(activity.name),
                    }
                }

    #lancer popup pour choisir activité à s'inscrire
    @api.multi
    def choose_queue_to_register(self):
        """ launch wizard to choose activity queue to register in"""
        self.ensure_one()
        member_id = self[0]
        #lancer le wizard avec le membre actuel
        return {
            'name'      : _('Choose the activity to register in'),
            'type'      : 'ir.actions.act_window',
            'res_model' : 'golem.activity.queue.choose.wizard',
            'view_mode': 'form',
            'context' : {'default_member_id' : member_id.id},
            'target': 'new',
        }
