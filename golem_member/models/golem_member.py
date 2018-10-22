# -*- coding: utf-8 -*-
#
#    Copyright 2016-2018 Fabien Bourgeois <fabien@yaltik.com>
#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
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

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
_LOGGER = logging.getLogger(__name__)

def get_root_area(area_id):
    """ Get root area """
    if not area_id.parent_id:
        return area_id
    return get_root_area(area_id.parent_id)

def is_sub_area(area_id, parent_id):
    """ Check if parent is sub area """
    if parent_id.parent_id.id == area_id.id:
        return True
    if not parent_id.parent_id:
        return False
    return is_sub_area(area_id, parent_id.parent_id)

class PartnerArea(models.Model):
    """ Partner Area """
    _name = 'golem.partner.area'
    _description = 'Partner Area'
    _order = 'sequence asc, name asc'
    _sql_constraints = [('golem_partner_area_uniq',
                         'UNIQUE (name)',
                         _('This patner area has already been used.'))]

    name = fields.Char(required=True, index=True)
    sequence = fields.Integer()
    area_street_ids = fields.One2many('golem.partner.area.street', 'area_id',
                                      string='Street list')
    parent_id = fields.Many2one('golem.partner.area', string='Parent Territory',
                                domain="[('id', '!=', id)]")
    root_id = fields.Many2one('golem.partner.area', compute='_compute_root_id',
                              string='Root area')

    @api.depends('parent_id')
    def _compute_root_id(self):
        """ Compute root_id """
        for area in self:
            area.root_id = get_root_area(area)

    @api.constrains('parent_id')
    def check_parent_id(self):
        """ Check if parent is sub area """
        for area in self:
            if  is_sub_area(area, area.parent_id):
                err = _('The parent area is a sub area of the current area, '
                        'please change it.')
                raise ValidationError(err)


class GolemPartnerAreaStreet(models.Model):
    """ GOLEM Partner Area Street Management """
    _name = 'golem.partner.area.street'
    _description = 'GOLEM Partner Area Street'

    name = fields.Char(required=True)
    area_id = fields.Many2one('golem.partner.area', required=True, sring='Area',
                              index=True, auto_join=True, ondelete='set null')


class ResPartner(models.Model):
    """ GOLEM Member partner adaptations """
    _inherit = 'res.partner'

    @api.model
    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    nationality_id = fields.Many2one('res.country', 'Nationality',
                                     auto_join=True,
                                     default=_get_default_nationality_id)
    area_id = fields.Many2one(
        'golem.partner.area', index=True, auto_join=True, string='Area',
        help="Area, quarter... for statistics and activity price."
    )
    area_from_street = fields.Boolean(store=False, default=False)
    country_id = fields.Many2one(default=_get_default_nationality_id)

    # Gender overwriting : no need for 'other' choice
    gender = fields.Selection([('male', _('Male')), ('female', _('Female'))])

    member_id = fields.One2many('golem.member', 'partner_id', 'Service user',
                                readonly=True)
    is_service_user = fields.Boolean(compute='_compute_is_service_user')
    member_number = fields.Char(related='member_id.number')

    @api.depends('member_id')
    def _compute_is_service_user(self):
        """ Computes is member """
        for partner in self:
            partner.is_service_user = len(partner.member_id) > 0

    @api.multi
    def view_member(self):
        """ Go to member form """
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': 'golem.member',
                'view_mode': 'form',
                'res_id': self[0].member_id.id if self[0].member_id else False}

    @api.multi
    def create_golem_member(self):
        """ Member creation from partner form """
        self.ensure_one()
        gm_obj = self.env['golem.member']
        gm_obj.create({'partner_id': self[0].id})

    @api.constrains('street')
    def save_street(self):
        """ Save street if no exist """
        for member in self:
            if member.street and not member.area_from_street:
                mstreet = member.street.strip()
                street_id = self.env['golem.partner.area.street'].search(
                    [('name', 'ilike', mstreet)]
                )
                if not street_id:
                    self.env['golem.partner.area.street'].create(
                        {'name': mstreet, 'area_id': member.area_id.id}
                    )

class GolemMembershipInvoice(models.TransientModel):
    """ GOLEM Membership Invoice adaptations """
    _inherit = 'golem.membership.invoice'

    @api.multi
    def membership_invoice(self):
        """ Extend invoice generation with number generation """
        self.ensure_one()
        res = super(GolemMembershipInvoice, self).membership_invoice()
        if self.partner_id.member_id:
            self.partner_id.member_id.generate_number()
        return res


class GolemMember(models.Model):
    """ GOLEM Member model """
    _name = 'golem.member'
    _description = 'GOLEM Member'
    _inherit = 'mail.thread'
    _inherits = {'res.partner': 'partner_id'}
    _sql_constraints = [('golem_member_number_manual_uniq',
                         'UNIQUE (number_manual)',
                         _('This member number has already been used.'))]

    partner_id = fields.Many2one('res.partner', required=True, index=True,
                                 ondelete='cascade')

    @api.model
    def default_season(self):
        """ Get default season """
        domain = [('is_default', '=', True)]
        return self.env['golem.season'].search(domain, limit=1)

    number_name = fields.Char('Member computed name', compute='_compute_number_name')
    number = fields.Char('Member number', store=True, readonly=True)
    number_manual = fields.Char('Manual number', size=50, index=True,
                                help='Manual number overwriting automatic '
                                'numbering')
    pictures_agreement = fields.Boolean('Pictures agreement?')
    electronic_processing_agreement = fields.Boolean('Electronic Processing Agreement?',
                                                     default=True)
    opt_out_sms = fields.Boolean('Out of SMS campaigns?',
                                 help='If this field has been checked, it '
                                 'tells that the user refuses to receive SMS')
    season_ids = fields.Many2many('golem.season', string='Seasons',
                                  required=True, default=default_season,
                                  auto_join=True, ondelete='restrict')
    is_default = fields.Boolean('Default season?',
                                compute='_compute_is_default',
                                search='_search_is_default')
    is_number_manual = fields.Boolean('Is number manual?', store=False,
                                      compute='_compute_is_number_manual')

    @api.onchange('country_id')
    def onchange_country_domain_state(self):
        """ On country change : adapts state domain """
        member = self[0]
        if member.country_id:
            return {
                'domain': {'state_id': [('country_id', '=', member.country_id.id)]}
            }
        return {'domain': {'state_id': []}}

    @api.depends('number', 'name')
    def _compute_number_name(self):
        """ Computes a name composed with number and name """
        for member in self:
            vals = []
            if member.number:
                vals.append(member.number)
            if member.name:
                vals.append(member.name)
            member.number_name = u' - '.join(vals)

    @api.depends('season_ids')
    def _compute_is_default(self):
        """ Computes is current according to seasons """
        default_s = self.default_season()
        for member in self:
            member.is_default = default_s in member.season_ids

    @api.multi
    def _search_is_default(self, operator, value):
        """ Search function for is default """
        if operator in ('in', '='):
            operator = '=' if value else '!='
        elif operator in ('not in', '!='):
            operator = '!=' if value else '='
        else:
            err = _('Unsupported operator for defautl season search')
            raise NotImplementedError(err)
        return [('season_ids', operator, self.default_season().id)]

    @api.depends('number')
    def _compute_is_number_manual(self):
        conf = self.env['ir.config_parameter']
        is_num_man = (conf.get_param('golem_numberconfig_isautomatic') == '0')
        self.update({'is_number_manual': is_num_man})

    @api.onchange('street')
    def onchange_street(self):
        """ Area auto assignement """
        for member in self:
            mstreet = member.street.strip() if member.street else False
            if mstreet and not member.area_id:
                street_id = self.env['golem.partner.area.street'].search(
                    [('name', 'ilike', mstreet)], limit=1
                )
                if street_id:
                    member.area_id = street_id.area_id
                    member.area_from_street = True

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
                    season.write({'member_counter': season.member_counter})
                    pkey = 'golem_numberconfig_prefix'
                    pfx = conf.get_param(pkey, '')
                    number = u'{}{}'.format(pfx, unicode(season.member_counter))
                    data = {'member_id': member.id,
                            'season_id': season.id,
                            'number': number}
                    member_num = member_number_obj.create(data)
                    season.member_counter += 1
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
            last = int(conf.get_param('golem_number_counter', 1))
            pfx = conf.get_param('golem_numberconfig_prefix', '')
            number = pfx + str(last)
            data = {'member_id': self[0].id,
                    'season_id': None,
                    'number': number}
            member_num = member_number_obj.create(data)
            last += 1
            conf.set_param('golem_number_counter', str(last))
        else:
            member_num = member_num[0]
        return member_num.number

    @api.multi
    def generate_number(self):
        """ Computes number according to pre-existing number and chosen
        seasons """
        conf = self.env['ir.config_parameter']
        isauto = conf.get_param('golem_numberconfig_isautomatic') == '1'
        isperseason = conf.get_param('golem_numberconfig_isperseason') == '1'
        isfornew = conf.get_param('golem_numberconfig_isfornewmembersonly') == '1'
        for member in self.filtered(lambda m: m.membership_state != 'none'):
            if not isauto or (isfornew and member.number_manual):
                member.number = member.number_manual
            else:
                if isperseason:
                    member.number = member.generate_number_perseason()
                else:
                    member.number = member.generate_number_global()

    @api.multi
    def write(self, vals):
        """ Number generation after updates """
        res = super(GolemMember, self).write(vals)
        if 'season_ids' in vals or 'number_manual' in vals:
            self.generate_number()
        return res


class GolemMemberNumber(models.Model):
    """ GOLEM Member Numbers """
    _name = 'golem.member.number'
    _description = 'GOLEM Member Numbers'

    name = fields.Char(compute='_compute_name')
    member_id = fields.Many2one('golem.member', string='Member', index=True,
                                required=True, ondelete='cascade',
                                auto_join=True)
    season_id = fields.Many2one('golem.season', string='Season', index=True,
                                auto_join=True)
    number = fields.Char(index=True, readonly=True)

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
    number_from = fields.Integer('First number', default=1,
                                 help='Number starting from, default to 1')

    @api.multi
    def apply_config(self):
        """ Apply new configuration """
        self.ensure_one()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_numberconfig_isautomatic', self.is_automatic)
        conf.set_param('golem_numberconfig_isperseason', self.is_per_season)
        conf.set_param('golem_numberconfig_prefix', self.prefix or '')
        if self.number_from:
            _LOGGER.warning('New number_from %s', self.number_from)
            conf.set_param('golem_number_counter', unicode(self.number_from))
            self.env['golem.season'].search([]).write({
                'member_counter': self.number_from
            })

    @api.multi
    def apply_nocompute(self):
        """ Apply new configuration only for new members (keep old numbers) """
        self.ensure_one()
        self.apply_config()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_numberconfig_isfornewmembersonly', '1')

    @api.multi
    def apply_recompute(self):
        """ Recomputes all member numbers according to new configuration """
        self.ensure_one()
        self.apply_config()
        conf = self.env['ir.config_parameter']
        conf.set_param('golem_numberconfig_isfornewmembersonly', '0')
        self.env['golem.member.number'].search([]).unlink()
        self.env['golem.season'].search([]).write({
            'member_counter': int(self.number_from)
        })
        member_obj = self.env['golem.member']
        member_obj.search([('membership_state', '=', 'none')]).write({'number': False})
        member_obj.search([('membership_state', '!=', 'none')]).generate_number()
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class MergePartnerAutomatic(models.TransientModel):
    """ Merge Partner Automatic adaptations """
    _inherit = 'base.partner.merge.automatic.wizard'

    @api.multi
    def action_merge(self):
        """ Merge adaptations : warn if there is a member """
        for merge in self:
            for partner in merge.partner_ids:
                if partner.member_id:
                    emsg = _('GOLEM Members merge has not been implemented yet. '
                             'Please only merge partners, not members, or delete '
                             'GOLEM Members manually before merging.')
                    raise UserError(emsg)
        return super(MergePartnerAutomatic, self).action_merge()
