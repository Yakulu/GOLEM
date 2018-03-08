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

""" GOLEM Activity Queue """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemActivityQueue(models.Model):
    """ GOLEM Activity Queue """
    _name = 'golem.activity.queue'
    _order = 'sequence asc, id asc'
    _description = 'GOLEM Activity Queue'
    _sql_constraints = [('golem_activity_queue_uniq', 'UNIQUE (member_id, activity_id)',
                         _('This member has already been registered for the queue.'))]

    member_id = fields.Many2one('golem.member', required=True,
                                string='Member', ondelete='cascade',
                                index=True)
    activity_id = fields.Many2one('golem.activity', required=True,
                                  string='Activity', ondelete='cascade',
                                  index=True)
    season_id = fields.Many2one(related='activity_id.season_id')
    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current', store=True)

    places_remain = fields.Integer(related='activity_id.places_remain')
    sequence = fields.Integer()

    @api.constrains('member_id', 'activity_id')
    def check_member_registration(self):
        """ Forbid registration in queue when member is already registred in the
        activity """
        for queue in self:
            if queue.activity_id in \
                queue.member_id.activity_registration_all_ids.mapped('activity_id'):
                raise ValidationError(_('The member your trying to add to the queue'
                                        ' is already registered for this activity'))
