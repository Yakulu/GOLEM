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

""" GOLEM Activity Registration """

from odoo import models, fields, api, _

class GolemActivityRegistration(models.Model):
    """ GOLEM Activity Registration """
    _inherit = 'golem.activity.registration'

    @api.constrains('member_id')
    def _check_member_reliability(self):
        """ Forbid registration when user doesn't have a valide membership """
        for reg in self:
            if reg.activity_id.only_for_subscriber:
                if reg.member_id.membership_state in ['none', 'canceled', 'old']:
                    emsg = _('Subscription can not be executed : the targeted '
                             'activity is only for subscriber.')
                    raise models.ValidationError(emsg)
