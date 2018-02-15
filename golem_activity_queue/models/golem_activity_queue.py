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

""" GOLEM activities related models """

from odoo import models, fields, api, _

class GolemActivity(models.Model):
    """ GOLEM Activity """
    _name = 'golem.activity'

    #ajout d'un champs O2M vers activity_id
    activity_queue_id = fields.One2many('golem.activity.queue', 'activity_id')
    # un boolen pour determiner si une fille d'attente est autorisé
    allows_queue = fields.Boolean(required=False)

class GolemActivityQueue(models.Model):
    """ GOLEM Activity Queue """
    _name = 'golem.activity.queue'
    _description = 'GOLEM Activity Queue'

    activity_id = fields.Many2one('golem.activity', required=True)
    season_id = fields.Many2one('golem.season', related='golem.activity.season_id')
    member_id = fields.Many2one('golem.member', required=True)
