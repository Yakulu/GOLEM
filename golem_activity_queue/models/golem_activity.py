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

class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'

    activity_queue_ids = fields.One2many('golem.activity.queue',
                                         'activity_id', 'Pending registration')
    queue_allowed = fields.Boolean(default=True, readonly=True)
    auto_registration_from_queue = fields.Boolean(default=True, readonly=True)
    queue_activity_number = fields.Integer(compute="_compute_queue_activity_number",
                                           store=True, string='Pending registration number')

    @api.multi
    def auto_registration_toggle(self):
        """ switch registration from queue mode """
        for activity in self:
            activity.auto_registration_from_queue = not activity.auto_registration_from_queue

    @api.multi
    def queue_allowed_toggle(self):
        """ Toggle queue_alowed boolean """
        self.ensure_one()
        activity = self[0]
        if activity.queue_allowed:
            if len(activity.activity_queue_ids) > 0:
                activity.activity_queue_ids.unlink()
            activity.write({'queue_allowed': False,
                            'auto_registration_from_queue': False})
        else:
            return {
                'name': _('Choose the activity to register in'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.activity.automated.queue.activate.wizard',
                'view_mode': 'form',
                'context': {'default_activity_id' : activity.id},
                'target': 'new',
            }

    @api.multi
    def register_from_queue(self):
        """ Registers from queue """
        for activity in self:
            queues = activity.activity_queue_ids
            if activity.queue_activity_number < activity.places_remain:
                queues = queues[0:activity.queue_activity_number]
            else:
                queues = queues[0:activity.places_remain]
            for queue in queues:
                values = {'activity_id' : queue.activity_id.id,
                          'member_id' : queue.member_id.id}
                self.env['golem.activity.registration'].create(values)
                queue.unlink()

    @api.constrains('activity_registration_ids')
    def handle_queue_at_register(self):
        """ Remove member from queue if he has been registered directly in
        activity (only for manual queue processing) """
        for activity in self:
            member_ids = activity.activity_registration_ids.mapped('member_id.id')
            queues_to_remove = activity.activity_queue_ids.filtered(
                lambda q: q.member_id.id in member_ids)
            queues_to_remove.unlink()

    @api.constrains('activity_queue_ids', 'activity_registration_ids',
                    'places_remain', 'queue_allowed', 'queue_activity_number',
                    'auto_registration_from_queue')
    def automated_register_from_queue(self):
        """automated registration from queue"""
        for activity in self:
            if (activity.places_remain and activity.queue_allowed and
                    activity.queue_activity_number > 0 and
                    activity.auto_registration_from_queue):
                activity.register_from_queue()

    @api.depends('activity_queue_ids')
    def _compute_queue_activity_number(self):
        """ compute number of queue registration for activity"""
        for activity in self:
            activity.queue_activity_number = len(activity.activity_queue_ids)

    @api.onchange('activity_registration_ids')
    def _check_registration_number(self):
        for activity in self:
            # Needed to ensure that we are negative in places
            activity._compute_places_remain()
            if activity.places_remain < 0 and activity.queue_allowed:
                message = _('No remaining place for the activity : {}, please'
                            ' discard changes and register in the queue.')
                return {
                    'warning' : {
                        'title' : _('Warning'),
                        'message': message.format(activity.name),
                    }
                }
            elif activity.places_remain > 0 and  activity.queue_activity_number > 0:
                if activity.auto_registration_from_queue:
                    warning_message = _('There is a free place for the activity'
                                        ' : {}, once you save it will be filled'
                                        ' by the first member from queue')
                else:
                    warning_message = _('There is a free place for the activity'
                                        ' : {}, you may fill it manually from '
                                        'the queue')
                return {
                    'warning' : {
                        'title' : _('Warning'),
                        'message': warning_message.format(activity.name)
                        }
                    }
