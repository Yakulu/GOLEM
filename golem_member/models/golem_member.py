# -*- coding: utf-8 -*-
#
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

""" GOLEM Members """

from odoo import models, fields, api, _


class ResPartner(models.Model):
    """ GOLEM Member partner adaptations """
    _inherit = 'res.partner'

    @api.model
    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    nationality_id = fields.Many2one('res.country', 'Nationality',
                                     default=_get_default_nationality_id)
    country_id = fields.Many2one(default=_get_default_nationality_id)

    # Gender overwriting : no need for 'other' choice
    gender = fields.Selection([('male', _('Male')), ('female', _('Female'))])

    member_id = fields.One2many('golem.member', 'partner_id', 'GOLEM Member',
                                readonly=True)
    member_number = fields.Char('Member number', related='member_id.number')

    @api.multi
    def create_golem_member(self):
        """ Member creation from partner form """
        self.ensure_one()
        gm_obj = self.env['golem.member']
        gm_obj.create({'partner_id': self[0].id})


class GolemMember(models.Model):
    """ GOLEM Member model """
    _name = 'golem.member'
    _description = 'GOLEM Member'
    _inherit = 'mail.thread'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, index=True,
                                 ondelete='cascade')

    @api.model
    def _default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain, limit=1)

    number = fields.Char('Member number', store=True, readonly=True)
    number_manual = fields.Char('Manual number', size=50, index=True,
                                help='Manual number overwriting automatic '
                                'numbering')
    pictures_agreement = fields.Boolean('Pictures agreement?')
    opt_out_sms = fields.Boolean('Out of SMS campaigns?',
                                 help='If this field has been checked, it '
                                 'tells that the user refuses to receive SMS')
    season_ids = fields.Many2many('golem.season', string='Seasons',
                                  required=True, default=_default_season,
                                  ondelete='restrict')
    is_current = fields.Boolean('Current user?', default=False, readonly=True,
                                store=True, compute='_compute_is_current')
    is_number_manual = fields.Boolean('Is number manual?', store=False,
                                      compute='_compute_is_number_manual')

    _sql_constraints = [('golem_member_number_manual_uniq',
                         'UNIQUE (number_manual)',
                         _('This member number has already been used.'))]

    @api.multi
    @api.depends('season_ids')
    def _compute_is_current(self):
        """ Computes is current according to seasons """
        default_s = self._default_season()
        for member in self:
            member.is_current = default_s in member.season_ids

    @api.multi
    @api.depends('number')
    def _compute_is_number_manual(self):
        conf = self.env['ir.config_parameter']
        is_num_man = (conf.get_param('golem_numberconfig_isautomatic') == '0')
        self.is_number_manual = is_num_man

    @api.multi
    def generate_number_perseason(self):
        """ Number generation in case of per season configuration """
        res = None
        conf = self.env['ir.config_parameter']
        member_number_obj = self.env['golem.member.number']
        for member in self:
            for season in member.season_ids:
                domain = ['&',
                          ('member_id', '=', member.id),
                          ('season_id', '=', season.id)]
                member_num = member_number_obj.search(domain)
                if not member_num:
                    season.member_counter += 1
                    season.write({'member_counter': season.member_counter})
                    pkey = 'golem_numberconfig_prefix'
                    pfx = conf.get_param(pkey, '')
                    number = pfx + str(season.member_counter)
                    data = {'member_id': member.id,
                            'season_id': season.id,
                            'number': number}
                    member_num = member_number_obj.create(data)
                if season.is_default:
                    res = member_num.number
        return res

    @api.multi
    def generate_number_global(self):
        """ Number generation in case of global configuration """
        self.ensure_one()
        conf = self.env['ir.config_parameter']
        domain = ['&',
                  ('member_id', '=', self[0].id),
                  ('season_id', '=', None)]
        member_number_obj = self.env['golem.member.number']
        member_num = member_number_obj.search(domain)
        if not member_num:
            last = int(conf.get_param('golem_number_counter', 0))
            last += 1
            conf.set_param('golem_number_counter', str(last))
            pfx = conf.get_param('golem_numberconfig_prefix', '')
            number = pfx + str(last)
            data = {'member_id': self[0].id,
                    'season_id': None,
                    'number': number}
            member_num = member_number_obj.create(data)
        return member_num.number

    @api.multi
    def generate_number(self):
        """ Computes number according to pre-existing number and chosen
        seasons """
        conf = self.env['ir.config_parameter']
        for member in self:
            if conf.get_param('golem_numberconfig_isautomatic') == '0':
                member.number = member.number_manual
            else:
                if conf.get_param('golem_numberconfig_isperseason') == '1':
                    member_num = member.generate_number_perseason()
                else:
                    member_num = member.generate_number_global()
                if member_num:
                    member.number = member_num[0]

    @api.model
    def create(self, values):
        """ Number generation after creation """
        new_member = super(GolemMember, self).create(values)
        new_member.generate_number()
        return new_member

    @api.multi
    def write(self, values):
        """ Number generation after updates """
        res = super(GolemMember, self).write(values)
        if 'season_ids' in values or 'number_manual' in values:
            self.generate_number()
        return res


class GolemMemberNumber(models.Model):
    """ GOLEM Member Numbers """
    _name = 'golem.member.number'
    _description = 'GOLEM Member Numbers'

    name = fields.Char('Name', compute='_compute_name')
    member_id = fields.Many2one('golem.member', string='Member', index=True,
                                required=True, ondelete='cascade',
                                auto_join=True)
    season_id = fields.Many2one('golem.season', string='Season', index=True,
                                auto_join=True)
    number = fields.Char('Number', index=True, readonly=True)

    @api.multi
    @api.depends('season_id')
    def _compute_name(self):
        for number in self:
            number.name = number.season_id.name


class GolemNumberConfig(models.TransientModel):
    """ Configuration for number computing """
    _name = 'golem.member.numberconfig'
    _description = 'Configuration for number computing'

    @api.model
    def _default_is_automatic(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_isautomatic', '1')

    @api.model
    def _default_is_per_season(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_isperseason', '0')

    @api.model
    def _default_prefix(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('golem_numberconfig_prefix', '')

    is_automatic = fields.Selection([('1', _('Yes')), ('0', _('No'))],
                                    string='Computed automatically?',
                                    default=_default_is_automatic)
    is_per_season = fields.Selection([('1', _('Yes')), ('0', _('No'))],
                                     string='Per season number?',
                                     default=_default_is_per_season)
    prefix = fields.Char('Optional prefix', default=_default_prefix)

    @api.multi
    def apply_config(self):
        """ Apply new configuration """
        self.ensure_one()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_numberconfig_isautomatic', self.is_automatic)
        conf.set_param('golem_numberconfig_isperseason', self.is_per_season)
        conf.set_param('golem_numberconfig_prefix', self.prefix or '')

    @api.multi
    def apply_recompute(self):
        """ Recomputes all member numbers according to new configuration """
        self.ensure_one()
        self.apply_config()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_number_counter', '0')
        self.env['golem.member.number'].search([]).unlink()
        self.env['golem.season'].search([]).write({'member_counter': 0})
        self.env['golem.member'].search([]).generate_number()
