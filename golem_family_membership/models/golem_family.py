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

""" GOLEM Families Adaptations"""

from odoo import models, api, _


class GolemFamily(models.Model):
    """ GOLEM Family Adaptations """
    _inherit = 'golem.family'

    @api.multi
    def family_membership(self):
        """ Wizard call for family membership """
        self.ensure_one()
        family = self[0]
        return {
            'name' : _('Please fill the family membership form'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'golem.membership.invoice',
            'context': {'default_family_id': family.id},
            'view_mode': 'form',
            'target': 'new'
            }
