# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Payment models """

from odoo import models, fields, api, _

class AccountPayment(models.Model):
    """ Add number bank check"""
    _inherit = 'account.payment'
    reference = fields.Char(string='Payment reference')

class GolemPaymentScheduleDay(models.Model):
    """ Schedule day simple model """
    _name = 'golem.payment.schedule.day'
    _rec_name = 'day'
    _sql_constraints = [('golem_payment_schedule_day_uniq', 'UNIQUE (day)',
                         _('Day must be unique.'))]

    day = fields.Date(required=True, index=True)


class GolemPaymentSchedule(models.Model):
    """ GOLEM Payment Schedule """
    _name = 'golem.payment.schedule'
    _description = 'GOLEM Payment Schedule'
    _order = 'season_id desc'

    name = fields.Char(required=True)
    day_ids = fields.Many2many('golem.payment.schedule.day', string='Days')
    occurences = fields.Integer(compute='_compute_occurences')

    season_id = fields.Many2one('golem.season', 'Season', required=True)


    @api.depends('day_ids')
    def _compute_occurences(self):
        """ Computes number of occurences """
        for schedule in self:
            schedule.occurences = len(schedule.day_ids)
