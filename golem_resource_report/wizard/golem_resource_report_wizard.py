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

""" GOLEM Resources Report Wizard """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemResourceReportWizard(models.TransientModel):
    """GOLEM Report Wizard : Choose report parameters """
    _name = "golem.resource.report.wizard"

    resource_ids = fields.Many2many('golem.resource')
    date_start = fields.Datetime(required=True)
    date_stop = fields.Datetime(required=True)

    @api.multi
    def print_resource_report(self):
        """ Print Report """
        self.ensure_one()
        record = self[0]
        start_date = fields.Datetime.from_string(record.date_start)
        stop_date = fields.Datetime.from_string(record.date_stop)
        if start_date > stop_date:
            raise ValidationError(_('Stop Date cannot be set before Start Date.'))
        else:
            data = self.read(
                ['resource_ids', 'date_start', 'date_stop'])[0]
            return self.env['report'].get_action(
                self, 'golem_resource_report.golem_reservation_report',
                data=data)
