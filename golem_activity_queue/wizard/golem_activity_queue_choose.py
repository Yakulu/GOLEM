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

""" GOLEM Resources management """

from odoo import models, fields, api, _

class GolemActivityQueueChooseWizard(models.TransientModel):
    """GOLEM Resource wizard : rchoose activity queue to register in """
    _name = "golem.activity.queue.choose.wizard"

    activity_id = fields.Many2one("golem.activity")


    def ChooseActivity(self):
        self.ensure_one()
        activityQueue = self[0]
        return {
            'name'      : _('Register in the queue'),
            'type'      : 'ir.actions.act_window',
            'res_model' : 'golem.activity.queue',
            'view_mode': 'tree',#
            'context' :{'default_activity_id' : activityQueue.activity_id.id},
            'domain' : [('activity_id', '=',activityQueue.activity_id.id )],# activity_id.name)],#"('activity_id', '=', True)"
            'flags': {'action_buttons': True},
            'target': 'new',
        }
