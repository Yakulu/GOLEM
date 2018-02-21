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

class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'


    #ajout d'un champs O2M vers activity_id de golem.activity.queue
    activity_queue_ids = fields.One2many('golem.activity.queue',
                        'activity_id','Pending registration')
    # un boolen pour determiner si une fille d'attente est autorisé
    queue_allowed = fields.Boolean(default=True)
    #ajout d'un champs pour calculer le nombre d'inscription en file d'attente
    queue_activity_number = fields.Integer(compute="_queue_activity_number",
                            store=True , string='Pending registration number')


    @api.multi
    def _queue_activity_number(self):
        for activity in self:
            activity.queue_activity_number = len(activity.activity_queue_ids)

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



    @api.onchange('activity_registration_ids')
    def _checkRemain(self):
        if len(self.activity_registration_ids) > self.places and self.queue_allowed:
            return {
                'warning' : {
                    'title' : _('Warning'),
                    'message': _('No remaining place, please register in the queue'),
                }
            }

    """
    @api.multi
    @api.constrains('places_remain')
    def _check_remaining_places(self):
        #Forbid inscription when there is no more place
        for activity in self:
            if activity.places_remain < 5:

                if self.queue_allowed:
                    print "__________________________ test ______________________"
                    return {
                        'name'      : _('Do you want to add your registration to the queue?'),
                        'type'      : 'ir.actions.act_window',
                        'res_model' : 'golem.activity.queue',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'target': 'new',
                        }
                    print "________________________________test 2 __________________"
                    raise models.ValidationError("erreur")


                else:
                    emsg = _('Sorry, there is no more place man !')
                    raise models.ValidationError(emsg)
"""
