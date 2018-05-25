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

""" Golem Reservation Report """

import time
from random import randint
from odoo import models, fields, api

# FIXME: usage of Odoo  fields will be needed for i18n awareness

def get_client_color(partner_number):
    """ Get Client Color """
    colors = ['#FFFF5B', '#81EC54', '#47C8C8', '#FB5A66', '#E8E750',
              '#CF4ACF', '#9655D2', '#FFA15B', '#5F68D5', '#60E652']
    color = "#000000"
    if partner_number < 10:
        color = colors[partner_number]
    else:
        red = randint(128, 255)
        green = randint(128, 255)
        blue = randint(128, 255)
        color = "#" +hex(red)[2:]+hex(green)[2:]+hex(blue)[2:]
    return color


class GolemResevationReport(models.AbstractModel):
    """ Golem Reservation Report """
    _name = 'report.golem_resource_report.golem_reservation_report'
    _description = 'Golem Reservation Report'

    def get_data(self, data):
        """ Get Resevation Data """
        domain = [('date_start', '>', data['date_start']),
                  ('date_stop', '<', data['date_stop']),
                  ('resource_id', 'in', data['resource_ids'])]
        reservations = self.env['golem.resource.reservation'].search(domain, order='date_start')
        total_reservations = len(reservations)
        resources = {r.resource_id.id: r.resource_id.name for r in reservations}
        days = sorted(list(set(reservations.mapped('day_start'))))

        partner_ids = reservations.mapped('partner_id.id')
        partner_colors = {}
        partner_number = 0
        for partner_id in partner_ids:
            partner_colors[str(partner_id)] = get_client_color(partner_number)
            partner_number += 1

        res = {} # List of multi-levels : group by resource, then, day_start
        for reservation in reservations:
            resource = reservation.resource_id.id
            day_start = reservation.day_start
            if not resource in res:
                res[resource] = {}
            if not day_start in res[resource]:
                res[resource][day_start] = []
            line = {
                'name': reservation.name,
                'resource_name': reservation.resource_id.name,
                'partner': reservation.partner_id.name,
                'date_start': reservation.date_start,
                'date_stop': reservation.date_stop,
                'day_start': reservation.day_start,
                'day_stop': fields.Datetime.from_string(reservation.date_stop).strftime('%Y-%m-%d'),
                'bgcolor': partner_colors[str(reservation.partner_id.id)],
                'note': reservation.note
            }
            res[resource][day_start].append(line)
        return res, total_reservations, resources, days

    @api.model
    def render_html(self, docids, data=None):
        """ Render HTML """
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        _data, total_reservations, resources, days = self.get_data(data)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'company': self.env.ref('base.main_company'),
            'time': time,
            'data': data,
            'date_start': '%s 00:00:00' % data['date_start'],
            'date_stop': '%s 23:59:59' % data['date_stop'],
            'total_reservations': total_reservations,
            'datas': _data,
            'resources': resources,
            'days': days
        }
        return self.env['report'] \
            .render('golem_resource_report.golem_reservation_report', docargs)
