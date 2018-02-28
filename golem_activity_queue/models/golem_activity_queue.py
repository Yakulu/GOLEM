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

""" GOLEM activities related models """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemActivityQueue(models.Model):
    """ GOLEM Activity Queue """
    _name = 'golem.activity.queue'
    _order = "sequence"
    _description = 'GOLEM Activity Queue'

    member_id = fields.Many2one('golem.member', required=True,
                                string='Member', ondelete='cascade',
                                index=True)
    activity_id = fields.Many2one('golem.activity', required=True,
                                  string='Activity', ondelete='cascade',
                                  index=True)
    season_id = fields.Many2one(related='activity_id.season_id')

    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current', store=True)
    #nombre de place disponible sur activité liée
    places_remain = fields.Integer(related='activity_id.places_remain')
    #activité liée est plein ou non
    is_activity_full = fields.Char(compute="_compute_is_activity_full", store=True)

    sequence = fields.Integer()

    _sql_constraints = [
        ('queue_uniq', 'UNIQUE (member_id, activity_id)',
         _('This member has already been registered for the queue.'))]


    # decider si l'activity liée est pleine ou non : pour group by sur la liste
    @api.depends('places_remain')
    def _compute_is_activity_full(self):
        """ Decide if activity is full or not """
        for record in self:
            if record.places_remain == 0:
                record.is_activity_full = "Full activity"
            else:
                record.is_activity_full = "Not full activity"

    @api.constrains('member_id', 'activity_id')
    def _check_member_registration(self):
        """ Forbid registration in queue when member is already registred in the
        activity """
        for queue in self:
            domain = [('member_id', '=', queue.member_id.id),
                      ('activity_id', '=', queue.activity_id.id)]
            #verifier si un enrigistrement avec le meme membre et activité est déja fait
            registrations = self.env['golem.activity.registration'].search(domain)
            #si oui lancer un erreur
            if len(registrations):
                raise ValidationError(_('The member your trying to add to the queue'
                                        ' is already registred for this activity'))
