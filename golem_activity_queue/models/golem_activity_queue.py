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

class GolemActivityQueue(models.Model):
    """ GOLEM Activity Queue """
    _name = 'golem.activity.queue'
    _description = 'GOLEM Activity Queue'

    activity_id = fields.Many2one('golem.activity', required=True, ondelete='cascade')
    season_id = fields.Many2one(related='activity_id.season_id')
    member_id = fields.Many2one('golem.member', required=True, ondelete='cascade')
    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current', store=True)

    def call_up_wizard(self):
        return {
            'name': 'Are you sure?',
            'type': 'ir.actions.act_window',
            'res_model': 'golem.queuepopup',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
             }
