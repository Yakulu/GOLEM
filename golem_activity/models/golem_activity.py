# -*- coding: utf-8 -*-

#    Copyright 2016 Fabien Bourgeois <fabien@yaltik.com>
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

from openerp import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Make default service for type
    type = fields.Selection(default='service')


class GolemActivity(models.Model):
    _name = 'golem.activity'
    _description = 'GOLEM Activity'
    _inherit = 'mail.thread'
    _inherits = {'product.template': 'product_id'}
    _rec_name = 'activity_name'

    season_id = fields.Many2one('golem.season', string='Seasons',
                                required=True)
    animator_id = fields.Many2one('res.partner', string="Animator",
                                  domain=[('is_company', '=', False)])
    places = fields.Integer('Places', default=0)
    is_overbooked = fields.Boolean('Allow overbook?', default=False)
    places_overbooked = fields.Integer('Places with overbook', default=0)

    @api.onchange('is_overbooked', 'places')
    def onchange_is_overbooked(self):
        for a in self:
            if a.places and a.is_overbooked:
                if not a.places_overbooked or (a.places_overbooked < a.places):
                    a.places_overbooked = a.places + 1

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

    date_start = fields.Date('Start date')
    date_end = fields.Date('End date')

    @api.constrains('date_start', 'date_end')
    def _check_period(self):
        """ Check if end date if after start date """
        for a in self:
            if a.date_start > a.date_end:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))

    @api.onchange('type')
    def onchange_type(self):
        """ Force service as type """
        for a in self:
            self.type = 'service'

    @api.onchange('season_id')
    def onchange_season_dates(self):
        """ Sets defaults dates according to season """
        for a in self:
            if a.season_id:
                if not a.date_start:
                    a.date_start = a.season_id.date_start
                if not a.date_end:
                    a.date_end = a.season_id.date_end

    is_current = fields.Boolean('Current season?', store=True, default=False,
                                compute='_compute_is_current')

    @api.depends('season_id')
    def _compute_is_current(self):
        """ Checks if activity is active for current season """
        domain = [('is_default', '=', True)]
        default_season = self.env['golem.season'].search(domain)
        for a in self:
            a.is_current = (default_season == a.season_id)

    activity_name = fields.Char('Name', compute='_compute_name', store=True,
                                index=True)

    @api.depends('name', 'default_code')
    def _compute_name(self):
        """ Provide a better displayed name """
        for a in self:
            activity_name = unicode(a.name)
            if a.default_code:
                activity_name = u'[{}] {}'.format(a.default_code,
                                                  activity_name)
            a.activity_name = activity_name
