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

""" GOLEM Season adaptations """

from odoo import models, api


class GolemSeason(models.Model):
    """ GOLEM Season adaptations """
    _inherit = 'golem.season'

    @api.multi
    def do_default_season(self):
        """ Add number regenration in some cases """
        self.ensure_one()
        res = super(GolemSeason, self).do_default_season()
        all_members = self.env['golem.member'].search([])
        conf = self.env['ir.config_parameter']
        if conf.get_param('golem_numberconfig_isautomatic') == '1' and \
                conf.get_param('golem_numberconfig_isperseason') == '1':
            all_members.generate_number()
        return res
