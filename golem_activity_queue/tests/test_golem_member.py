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

""" GOLEM member testing """


from odoo.tests.common import TransactionCase
# from psycopg2 import IntegrityError


class TestGolemMember(TransactionCase):
    """ GOLEM member testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap member """
        super(TestGolemMember, self).setUp(*args, **kwargs)
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


    def test_member_creation(self):
        """ Test member creation """
        member1 = self.member1.create(self.data_member_1)
        #verification que le membre n'est inscrit en aucune attente
        self.assertFalse(member1.activity_queue_ids)


    def test_automated_registration(self):
        """ Test automated registration """
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
        #Verification que l'atente est le basculement automatique est aactivé
        self.assertTrue(activity.queue_allowed)
        self.assertTrue(activity.auto_registration_from_queue)
        #réduire le nombre de place sur activity  à 1
        activity.write({'places': 1})
        #enregistrement du membre 1 sur activity et memebre 2 sur attente
        activity.write({'activity_registration_ids': [(0, False, registration)]})
        activity.write({'activity_queue_ids': [(0, False, queue)]})
        #vérification des membre 1 sur registration et membre 2 sur attente
        self.assertEqual(activity.activity_registration_ids[0].member_id, member1)
        self.assertEqual(activity.activity_queue_ids[0].member_id, member2)
        #suppression du membre 1 de l'activity
        member1.write({'activity_registration_ids': [(2, member1.activity_registration_ids[0].id, False)]})
        #verifcation de la presence du membre 2 sur activity : basculement depuis attente
        self.assertEqual(activity.activity_registration_ids[0].member_id, member2)
        #verification de l'attente est vide
        self.assertFalse(activity.activity_queue_ids)
        print "test membre fini __________________________tn "
