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

""" GOLEM Resources management """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemResourceReportWizard(models.TransientModel):
    """GOLEM Resource wizard : refusal reason for a reservation """
    _name = "golem.resource.report.wizard"

    resource_ids = fields.Many2many('golem.resource')
    date_start = fields.Datetime(required=True)
    date_stop = fields.Datetime(required=True)

    @api.multi
    def print_report(self):
        for record in self:
            start_date = fields.Datetime.from_string(record.date_start)
            stop_date = fields.Datetime.from_string(record.date_stop)
            if start_date > stop_date:
                raise ValidationError(_("Stop Date cannot be set before \
                Start Date."))
            else:
                domain = [('date_start', '>', record.date_start),
                          ('date_stop', '<', record.date_stop),
                          ('resource_id', 'in', record.selected_resource_ids.ids)]
                data = self.env['golem.resource.reservation'].search(domain)
