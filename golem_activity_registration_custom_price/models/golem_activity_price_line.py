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

""" GOLEM Activity adaptations """

from odoo import models, fields, _


class GolemActivityPriceLine(models.Model):
    """ GOLEM Activity Price Line """
    _name = 'golem.activity.price.line'
    _description = 'GOLEM Activity Price Line'
    _order = 'activity_id asc, area_id asc, slice_id asc'
    _sql_constraints = [(
        'golem_activity_price_line_uniq', 'UNIQUE (activity_id, area_id, slice_id)',
        _('This activity, geo rule, FQ slice rule has already been used.')
    )]

    activity_id = fields.Many2one(
        'golem.activity', required=True, index=True, auto_join=True,
        ondelete='cascade'
    )
    area_id = fields.Many2one(
        'golem.partner.area', index=True, auto_join=True,
        string='Area', ondelete='cascade'
    )
    area_sequence = fields.Integer(related='area_id.sequence')
    slice_id = fields.Many2one(
        'golem.payment.rule.familyquotient.slice', index=True, auto_join=True,
        string='Family quotient slice', ondelete='cascade'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    price = fields.Monetary(required=True)
