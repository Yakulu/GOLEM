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

from openerp import models, fields, api, _


class GolemActivity(models.Model):
    _inherit = 'golem.activity'

    places_min = fields.Integer('Minimum places', default=0,
                                help='Minimum places to maintain the activity')
    is_overbooked = fields.Boolean('Allow overbook?', default=False)
    places_overbooked = fields.Integer('Places with overbook', default=0)

    @api.one
    @api.depends('places', 'is_overbooked', 'places_overbooked', 'places_used')
    def _compute_places_remain(self):
        if not self.is_overbooked:
            self.places_remain = self.places - self.places_used
        else:
            self.places_remain = self.places_overbooked - self.places_used

    @api.onchange('is_overbooked', 'places')
    def onchange_is_overbooked(self):
        for s in self:
            if s.places and s.is_overbooked:
                if not s.places_overbooked or (s.places_overbooked < s.places):
                    s.places_overbooked = s.places + 1

    @api.constrains('places', 'places_overbooked')
    def _check_places(self):
        """ Check integers are signed and overbooked to be superior than
        normal places """
        for v in self:
            for f in ['places', 'places_overbooked']:
                if v[f] < 0:
                    emsg = _('Number of places cannot be negative.')
                    raise models.ValidationError(emsg)
            if v.is_overbooked and (v.places_overbooked <= v.places):
                emsg = _('Overbooked places cannot be inferior than places')
                raise models.ValidationError(emsg)
