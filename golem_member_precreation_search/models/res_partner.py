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

""" GOLEM Contact """

from odoo import models, api, _

class ResPartner(models.Model):
    """ Res Partner extention """
    _inherit = 'res.partner'

    @api.multi
    def precreation_search(self):
        """ Precreation contact search """
        self.ensure_one()
        return {
            'name' : _('Please enter contact searched'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'golem.precreation.member.request.wizard',
            'view_mode': 'form',
            'target': 'new'
            }

    @api.multi
    def navigate_to_contact(self):
        """ Navigates to contact form, in edit mode """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Member',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self[0].id,
            'flags': {'initial_mode': 'edit'},
            'target': 'current'
        }
