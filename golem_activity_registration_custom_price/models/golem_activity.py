# -*- coding: utf-8 -*-

#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

""" GOLEM Activity adaptations """

from odoo import models, fields, api

class GolemActivity(models.Model):
    """ GOLEM Activity adaptations """
    _inherit = 'golem.activity'

    price_line_ids = fields.One2many('golem.activity.price.line',
                                     'activity_id', string='Price lines',
                                     copy=True)

    @api.multi
    def reset_price_combinations(self):
        """ Resets all combinations with default price """
        self.ensure_one()
        activity = self[0]
        activity.price_line_ids = [(6, False, [])] # Truncate existing
        activity.fill_price_combinations()

    @api.multi
    def fill_price_combinations(self):
        """ Fills all inexistent combinations prices from default one """
        self.ensure_one()
        activity = self[0]
        existing_combinations = [u'%s-%s' % (line.area_id.id, line.slice_id.id)
                                 for line in activity.price_line_ids]
        slice_ids = self.env['golem.payment.rule.familyquotient.slice'].search([])
        for area_id in self.env['golem.partner.area'].search([('parent_id', '=', False)]):
            for slice_id in slice_ids:
                combination = u'%s-%s' % (area_id.id, slice_id.id)
                if combination not in existing_combinations:
                    data = {'activity_id': activity.id, 'area_id': area_id.id,
                            'slice_id': slice_id.id, 'price': activity.list_price}
                    self.env['golem.activity.price.line'].create(data)
