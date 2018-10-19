# -*- coding: utf-8 -*-

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

""" Partner adaptations """

from odoo import models, fields, api


class Partner(models.Model):
    """ Partner adaptations """
    _inherit = 'res.partner'

    signup_token = fields.Char(groups="golem_base.group_golem_manager")
    signup_type = fields.Char(groups="golem_base.group_golem_manager")
    signup_expiration = fields.Datetime(groups="golem_base.group_golem_manager")

    @api.multi
    def write(self, vals):
        """ Overwrite native function to workaround admin only write on fields
        signup*, as it's impossible to overwrite groups attribute """
        if (('signup_token' in vals or 'signup_type' in vals or
                'signup_expiration' in vals)
                and self.env.user.has_group('golem_base.group_golem_manager')):
            return super(Partner, self.sudo()).write(vals)
        return super(Partner, self).write(vals)
