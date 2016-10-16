# -*- coding: utf-8 -*-

#    copyright 2016 fabien bourgeois <fabien@yaltik.com>
#
#    this program is free software: you can redistribute it and/or modify
#    it under the terms of the gnu affero general public license as
#    published by the free software foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    this program is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.

import json
import openerp.http as http
from openerp.http import request
from openerp.addons.web.controllers.main import CSVExport


class ExportGolemActivityMembers(CSVExport):

    @http.route('/web/export/golem/activity_members', type='http', auth='user')
    def export_csv_view(self, data):
        data = json.loads(data)
        FIELDS = ['number', 'lastname', 'firstname', 'contact_address', 'zip',
                  'city', 'birthdate_date', 'email', 'phone', 'mobile']
        aid = data.get('activity_id')
        a_model = request.env['golem.activity']
        activity = a_model.browse([aid])
        registrations = activity.activity_registration_ids
        rows = []
        for r in registrations:
            row = []
            for f in FIELDS:
                value = r.member_id.__getattribute__(f)
                row.append(value)
            rows.append(row)

        return request.make_response(
            self.from_data(FIELDS, rows),
            headers=[('Content-Disposition', 'attachment; filename="%s"'
                      % self.filename('gollem.activity')),
                     ('Content-Type', self.content_type)])
