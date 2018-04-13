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

import time

from random import randint
from odoo import models, api



class GolemResevationReport(models.AbstractModel):
    _name = 'report.golem_resource_report.golem_reservation_report'

    def get_total_reservation(self, data):
        domain = [('date_start', '>', data['date_start']),
                  ('date_stop', '<', data['date_stop']),
                  ('resource_id', 'in', data['resource_ids'])]
        return self.env['golem.resource.reservation'].search_count(domain)




    def get_resource(self, data):
        lst = []
        domain = [('date_start', '>', data['date_start']),
                  ('date_stop', '<', data['date_stop']),
                  ('resource_id', 'in', data['resource_ids'])]
        reservations = self.env['golem.resource.reservation'].search(domain, order='date_start')
        lst = reservations.mapped('resource_id.name')
        return lst

    def get_client_color(self, client_id):
        client_id *= 777777
        color = "#0" + str(client_id)
        color = color[:7]
        return color

    def get_data(self, data):
        lst = []
        domain = [('date_start', '>', data['date_start']),
                  ('date_stop', '<', data['date_stop']),
                  ('resource_id', 'in', data['resource_ids'])]
        reservations = self.env['golem.resource.reservation'].search(domain, order='date_start')
        res = {}
        for reservation in reservations:
            res = {
                'name': reservation.name,
                'resource_name': reservation.resource_id.name,
                'client': reservation.partner_id.name,
                'client_id': self.get_client_color(reservation.partner_id.id),
                'date_start': reservation.date_start,
                'date_stop': reservation.date_stop,
                'day_start': reservation.day_start
            }
            lst.append(res)
        return lst

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'data': data,
            'date_start': data['date_start'],
            'date_stop': data['date_stop'],
            'get_total_reservation': self.get_total_reservation(data),
            'get_data': self.get_data(data),
            'get_resource': self.get_resource(data),
        }
        return self.env['report'] \
            .render('golem_resource_report.golem_reservation_report', docargs)
