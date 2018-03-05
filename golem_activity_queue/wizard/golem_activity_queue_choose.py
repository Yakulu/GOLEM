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

from odoo import models, fields

class GolemActivityQueueChooseWizard(models.TransientModel):
    """GOLEM Resource wizard : rchoose activity queue to register in """
    _name = "golem.activity.queue.choose.wizard"

    activity_id = fields.Many2one("golem.activity")
    member_id = fields.Many2one("golem.member")


    # lancer liste editable d'inscription sur attente
    def register_in_queue(self):
        """ Choisir l'activité pour s'inscrire sur sa liste d'attente"""
        self.ensure_one()
        activity_queue = self[0]
        self.env['golem.activity.queue'].create({'member_id': activity_queue.member_id.id,
                                                 'activity_id': activity_queue.activity_id.id})
