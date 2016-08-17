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


class GolemMember(models.Model):
    _inherit = 'golem.member'

    activity_session_ids = fields.Many2many('golem.activity.session',
                                            string='Activities')


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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Make default service for type
    type = fields.Selection(default='service')


class GolemActivitySession(models.Model):
    _name = 'golem.activity.session'
    _description = 'GOLEM Activities Sessions'
    _inherit = 'mail.thread'
    _inherits = {'product.template': 'product_id'}
    _rec_name = 'session_name'

    _sql_constraints = [('golem_activity_session_places_signed',
                         'CHECK (places >= 0)',
                         _('Number of places cannot be negative.'))]

    product_id = fields.Many2one('product.template', required=True,
                                 ondelete='cascade')
    default_code = fields.Char(copy=True)  # Copy the default code

    @api.model
    def _default_name(self):
        """ Default name to activity name """
        d_aid = self.env.context.get('default_activity_id')
        aobj = self.env['golem.activity']
        return aobj.browse([d_aid]).name if d_aid else None

    image = fields.Binary(related='activity_id.image')
    categ_id = fields.Many2one(related='activity_id.categ_id', readonly=True)

    session_name = fields.Char('Name', compute='_compute_full_name',
                               store=True, index=True)

    @api.one
    @api.depends('name', 'default_code')
    def _compute_full_name(self):
        """ Provide a better displayed name """
        session_name = unicode(self.name)
        if self.default_code:
            session_name = u'[{}] {}'.format(self.default_code, session_name)
        self.session_name = session_name

    member_ids = fields.Many2many('golem.member', string='Members')
    type_of = fields.Selection([('activity', _('Activity')),
                                ('workshop', _('Workshop')),
                                ('training', _('Training'))],
                               default='activity', index=True, string='Type')

    @api.onchange('type_of')
    def onchange_type_of(self):
        for s in self:
            if s.type_of != 'activity':
                s.is_recurrent = False
            else:
                s.is_recurrent = True

    places_used = fields.Integer('Places used', compute='_compute_places_used')

    @api.one
    @api.depends('member_ids')
    def _compute_places_used(self):
        self.places_used = len(self.member_ids)

    # TODO: to link with calendar.event
    activity_id = fields.Many2one('golem.activity', string='Activity',
                                  required=True)

    animator_id = fields.Many2one('res.partner', string='Animator')
    is_current = fields.Boolean('Current season?',
                                related='activity_id.is_current')
    season_id = fields.Many2one(string='Season',
                                related='activity_id.season_id')

    @api.onchange('activity_id')
    def onchange_activity_id(self):
        """ Sets session name and animator as activity's one if empty """
        for s in self:
            if not s.name:
                s.name = s.activity_id.name
            if not s.default_code:
                s.default_code = s.activity_id.default_code
            if not s.animator_id:
                s.animator_id = s.activity_id.animator_id

    is_recurrent = fields.Boolean('Is recurrent ?', default=True,
                                  help='Work in progress')
    date_start = fields.Datetime('Start date')
    date_end = fields.Datetime('End date')

    @api.onchange('date_start')
    def onchange_date_start(self):
        """ Sets end date to start date if no start date """
        for s in self:
            if not s.date_end:
                s.date_end = s.date_start

    @api.constrains('date_start', 'date_end')
    def _check_date_period(self):
        """ Check if end date if after start date and if dates are included
        into main activity period"""
        for s in self:
            if not s.is_recurrent:
                if s.date_start > s.date_end:
                    emsg = _('Start of the session cannot be after end of the '
                             'session.')
                    raise models.ValidationError(emsg)
                if s.date_start < s.activity_id.date_start:
                    emsg = _('Start of the session cannot be before the start '
                             'of activity date')
                    raise models.ValidationError(emsg)
                if s.date_end > s.activity_id.date_end:
                    emsg = _('End of the session cannot be after the end of '
                             'activity date')
                    raise models.ValidationError(emsg)

    weekday = fields.Selection([('mon', _('Monday')),
                                ('tue', _('Tuesday')),
                                ('wed', _('Wednesday')),
                                ('thu', _('Thursday')),
                                ('fri', _('Friday')),
                                ('sat', _('Saturday')),
                                ('sun', _('Sunday'))])
    hour_start = fields.Float('Start time')
    hour_end = fields.Float('End time')

    @api.onchange('hour_start')
    def onchange_hour_start(self):
        """ Sets end hour to start hour if no start hour """
        for s in self:
            if s.hour_start and not s.hour_end:
                s.hour_end = s.hour_start + 1

    @api.constrains('hour_start', 'hour_end')
    def _check_hour_period(self):
        """ Check if end hour if after start hour """
        for s in self:
            if s.hour_start > s.hour_end:
                raise models.ValidationError(_('Start of the period cannot be '
                                               'after end of the period.'))

    places = fields.Integer('Places', default=0)
    places_remain = fields.Integer('Remaining places', store=True,
                                   compute='_compute_places_remain')

    @api.one
    @api.depends('places', 'member_ids')
    def _compute_places_remain(self):
        used = len(self.member_ids)
        self.places_remain = self.places - used

    @api.constrains('places_remain')
    def _check_remaining_places(self):
        """ Forbid inscription when there is no more place """
        for s in self:
            if s.places_remain < 0:
                emsg = _('Sorry, there is no more place !')
                raise models.ValidationError(emsg)
