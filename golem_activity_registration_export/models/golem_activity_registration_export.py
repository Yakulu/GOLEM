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

from json import dumps
from openerp import models, api


class GolemActivity(models.Model):
    _inherit = 'golem.activity'

    @api.multi
    def do_export_csv(self):
        """ Export basic data about members of the current activity to CSV """
        self.ensure_one()
        data = dumps({'activity_id': self.id})
        url = '/web/export/golem/activity_members?data={}'.format(data)
        print url
        return {'type': 'ir.actions.act_url', 'url': url, 'target': 'self'}
