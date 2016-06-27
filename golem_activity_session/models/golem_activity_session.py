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

    session_count = fields.Integer('Sessions',
                                   compute='_compute_session_count')

    @api.one
    def _compute_session_count(self):
        dmn = [('activity_id', '=', self.id)]
        cnt = self.env['golem.activity.session'].search_count(dmn)
        self.session_count = cnt

    @api.multi
    def button_session(self):
        self.ensure_one()
        return {'name': _('Activity Sessions'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.activity.session',
                'view_mode': 'tree,form',
                'context': {'default_activity_id': self.id,
                            'default_animator_id': self.animator_id.id},
                'domain': [('activity_id', '=', self.id)]}


class GolemActivitySession(models.Model):
    _name = 'golem.activity.session'
    _description = 'GOLEM Activities Sessions'

    name = fields.Char('Name', compute='_compute_name')

    @api.depends('activity_id', 'weekday')
    def _compute_name(self):
        for s in self:
            s.name = s.activity_id.activity_name

    # TODO: reucrrence etc... to link with calendar.event
    activity_id = fields.Many2one('golem.activity', string='Activité',
                                  required=True)
    animator_id = fields.Many2one('res.partner', string='Animator',
                                  required=True)
    is_recurrent = fields.Boolean('Is recurrent ?', default=False,
                                  help="Work in progress")
    weekday = fields.Selection([('mon', _('Monday')),
                                ('tue', _('Tuesday')),
                                ('wed', _('Wednesday')),
                                ('thu', _('Thursday')),
                                ('fri', _('Friday')),
                                ('sat', _('Saturday')),
                                ('sun', _('Sunday'))])
    hour_start = fields.Float('Start time')
    hour_end = fields.Float('End time')
    note = fields.Text('Note')

    @api.constrains('hour_start', 'hour_end')
    def _check_period(self):
        """ Check if end hour if after start hour """
        for s in self:
            if s.hour_start > s.hour_end:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))
