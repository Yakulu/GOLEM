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

""" Product adaptations """

from odoo import models, fields, api

class ProductTemplate(models.Model):
    """ Product Template adaptations """
    _inherit = 'product.template'

    season_id = fields.Many2one('golem.season', 'Linked season', index=True)

    @api.onchange('season_id')
    def onchange_season(self):
        """ Adapts period to selected season if needed """
        for product in self:
            if product.membership and product.season_id \
                and not product.membership_date_from:
                product.update({
                    'membership_date_from': product.season_id.date_start,
                    'membership_date_to': product.season_id.date_end
                })
