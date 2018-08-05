# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
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
from odoo.exceptions import ValidationError
from odoo.tools import formatLang

class AccountPayment(models.Model):
    """ Add number bank check"""
    _inherit = 'account.payment'
    reference = fields.Char(string='Payment reference')

class GolemPaymentScheduleDay(models.Model):
    """ Schedule day simple model """
    _name = 'golem.payment.schedule.day'
    _rec_name = 'day'
    _order = 'schedule_id asc,day asc'
    _sql_constraints = [('golem_payment_schedule_day_uniq',
                         'UNIQUE (day, schedule_id)',
                         _('Day must be unique.'))]

    day = fields.Date(required=True)
    schedule_id = fields.Many2one('golem.payment.schedule', required=True,
                                  auto_join=True, ondelete='cascade')


class GolemPaymentSchedule(models.Model):
    """ GOLEM Payment Schedule """
    _name = 'golem.payment.schedule'
    _description = 'GOLEM Payment Schedule'
    _order = 'season_id desc'

    name = fields.Char(required=True)
    day_ids = fields.One2many('golem.payment.schedule.day', 'schedule_id',
                              string='Days')
    day_display = fields.Char(compute='_compute_day_display', string='Days')
    occurences = fields.Integer(compute='_compute_occurences')
    season_id = fields.Many2one('golem.season', 'Season', required=True)

    @api.depends('day_ids')
    def _compute_day_display(self):
        """ Computes day display """
        for schedule in self:
            days = [fields.Date.from_string(d.day).strftime('%d/%m/%Y')
                    for d in schedule.day_ids]
            schedule.day_display = u', '.join(days)

    @api.depends('day_ids')
    def _compute_occurences(self):
        """ Computes number of occurences """
        for schedule in self:
            schedule.occurences = len(schedule.day_ids)

    @api.constrains('day_ids', 'season_id')
    def check_dates(self):
        """ Check date coherence """
        for schedule in self:
            if schedule.season_id.date_start:
                days = schedule.day_ids.mapped('day')
                for day in days:
                    season = schedule.season_id
                    if (day < season.date_start or day > season.date_end):
                        verr = _('Day %s is out of season period (%s-%s)'% \
                                 (day, season.date_start, season.date_end))
                        raise ValidationError(verr)
