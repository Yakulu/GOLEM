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

from odoo.tests.common import TransactionCase
from odoo.models import ValidationError


class TestGolemActivity(TransactionCase):
    """ GOLEM Activity Queue testing """

    def setUp(self):
        """ Bootstrap activity """
        super(TestGolemActivity, self).setUp()
        #création du saison
        self.season = self.env['golem.season'].sudo().create({'name': u'Season 1'})
        self.season.do_default_season()
        #préparation des données pour la création des membres
        self.data_member_1 = {'lastname': u'LAST1',
                              'firstname': u'First1',
                              'season_ids':[(4, self.season.id, False)]
                             }
        self.data_member_2 = {'lastname': u'LAST2',
                              'firstname': u'First2',
                              'season_ids':[(4, self.season.id, False)]
                             }
        self.member1 = self.env['golem.member']
        self.member2 = self.env['golem.member']
        #préparation des donnée pour la création de l'activité
        type_id = self.ref("golem_activity.golem_activity_type_activity")
        self.data_activity = {
            'name': u'Activity 1',
            'season_id': self.season.id,
            'type_id': type_id}
        self.activity = self.env['golem.activity']

    # test de creation d'activity et inistialisation des champs
    def test_activity_creation(self):
        """ Test creation of activity """
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)
        self.assertEqual(activity.queue_activity_number, 0)
        self.assertFalse(activity.activity_registration_ids)
        self.assertFalse(activity.activity_queue_ids)


    #test toggle auto_registration
    def test_auto_registration_toggle(self):
        """ Test Toggle Autoregistration from queue """
        activity = self.activity.create(self.data_activity)
        self.assertTrue(activity.auto_registration_from_queue)
        activity.auto_registration_toggle()
        self.assertFalse(activity.auto_registration_from_queue)
        activity.auto_registration_toggle()
        self.assertTrue(activity.auto_registration_from_queue)
    #test du queue_allowed toggle: en cas de désactivation queue doit etre vidé
    def test_queue_allowed_toggle(self):
        """ Test Toggle queue_allowed """
        #création de 2 membre est une activité
        member1 = self.member1.create(self.data_member_1)
        member2 = self.member2.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        #membre 1 inscrit sur activity
        registration = {
            'activity_id' : activity.id,
            'member_id' : member1.id
            }
        #memebre 2 inscrit sur attente
        queue = {
            'activity_id' : activity.id,
            'member_id' : member2.id
            }
        #Verification que l'atente est aactivé
        self.assertTrue(activity.queue_allowed)
        #réduire le nombre de place sur activity  à 1
        activity.write({'places': 1})
        #enregistrement du membre 1 sur activity et memebre 2 sur attente
        activity.write({'activity_registration_ids': [(0, False, registration)]})
        activity.write({'activity_queue_ids': [(0, False, queue)]})
        #desactivation de l'attente
        activity.queue_allowed_toggle()
        #verification que l'attente est désactivé et vidé
        self.assertFalse(activity.queue_allowed)
        self.assertFalse(activity.activity_queue_ids)
        #appel wizard pour activation de l'attente
        queue_activate_wizard_model = self.env['golem.activity.automated.queue.activate.wizard']
        queue_activate_wizard = queue_activate_wizard_model.create({'activity_id': activity.id})
        queue_activate_wizard.activate_queue()
        #verification de l'attente activité
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)

    #test de basculement automatique depuis queue
    def test_auto_registration(self):
        """ Test auto registration from queue """
        #création de 2 membre est une activité
        member1 = self.member1.create(self.data_member_1)
        member2 = self.member2.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        #réduire le nombre de place sur activity  à 1 et activation de queue et autoregistrement
        activity.write({'places': 1,
                        'queue_allowed': True,
                        'auto_registration_from_queue': True})
        #membre 1 inscrit sur activity
        registration = {
            'activity_id' : activity.id,
            'member_id' : member1.id
            }
        #memebre 2 inscrit sur attente
        queue = {
            'activity_id' : activity.id,
            'member_id' : member2.id
            }
        #enregistrement du membre 1 sur activity et memebre 2 sur attente
        activity.write({'activity_registration_ids': [(0, False, registration)]})
        activity.write({'activity_queue_ids': [(0, False, queue)]})
        #vérification du membre 1 sur registration et membre 2 sur attente
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        self.assertEqual(activity.activity_queue_ids[0].member_id, member2)
        #suppression du membre 1 de l'activity
        activity.write({'activity_registration_ids': [(2,
                                                       activity.activity_registration_ids[0].id,
                                                       False)]})
        #verifcation de la presence du membre 2 sur activity : basculement depuis attente
        self.assertEqual(activity.activity_registration_ids[0].member_id, member2)
        #verification de l'attente est vide
        self.assertFalse(activity.activity_queue_ids)
    # suppression du membre sur l'attente s'il sinscrit directement sur l'activity
    def test_delete_queue_member(self):
        """ Test Delete Queue member if they directly register """
        #création de 2 membre est une activité
        member1 = self.member1.create(self.data_member_1)
        member2 = self.member2.create(self.data_member_2)
        activity = self.activity.create(self.data_activity)
        #réduire le nombre de place sur activity  à 1 et activation de queue et autoregistrement
        activity.write({'places': 1,
                        'queue_allowed': True,
                        'auto_registration_from_queue': False})
        #membre 1 inscrit sur activity
        registration = {
            'activity_id' : activity.id,
            'member_id' : member1.id
            }
        #memebre 2 inscrit sur attente
        queue = {
            'activity_id' : activity.id,
            'member_id' : member2.id
            }
        #enregistrement du membre 1 sur activity et memebre 2 sur attente
        activity.write({'activity_registration_ids': [(0, False, registration)]})
        activity.write({'activity_queue_ids': [(0, False, queue)]})
        # vérification des inscriptions
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        self.assertEqual(activity.activity_queue_ids[0].member_id, member2)
        #suppression du membre 1 de l'activity
        activity.write({'activity_registration_ids': [(2,
                                                       activity.activity_registration_ids[0].id,
                                                       False)]})
        #inscription sur activity avec le membre sur queue
        activity.write({'activity_registration_ids': [(0, False, queue)]})
        #vérification queue vide
        self.assertFalse(activity.activity_queue_ids)
        #verification du membre 2 sur inscriptions
        self.assertEqual(activity.activity_registration_ids[0].member_id, member2)
