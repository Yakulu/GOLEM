# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Families """

from odoo import models, fields, api, _


class ResPartner(models.Model):
    """ Partner adaptations """
    _inherit = 'res.partner'

    family_member_ids = fields.One2many(related='family_id.member_ids')
    family_street = fields.Char(related='family_id.street')
    family_street2 = fields.Char(related='family_id.street2')
    family_zip = fields.Char(related='family_id.zip')
    family_city = fields.Char(related='family_id.city')
    family_state_id = fields.Many2one(related='family_id.state_id')
    family_country_id = fields.Many2one(related='family_id.country_id')
    family_phone = fields.Char(related='family_id.phone')
    family_mobile = fields.Char(related='family_id.mobile')
    family_email = fields.Char(related='family_id.email')
    family_website = fields.Char(related='family_id.website')

    family_id = fields.Many2one('golem.family', string='Family', index=True)
    family_role = fields.Many2one('golem.family.role', string='Role',
                                  index=True)
    family_count = fields.Integer(related='family_id.count')

    @api.multi
    def button_family_members(self):
        """ Go to family view, from partner """
        self.ensure_one()
        return {'name': _('Family Members'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.family',
                'view_mode': 'form',
                'res_id': self.family_id.id}

    @api.onchange('family_id')
    def onchange_family(self):
        """ Sets as family address if there was no precedence """
        for member in self:
            if member.family_id and not any((member.lastname, member.street, \
                                             member.street2, member.zip, member.city)):
                member.update({'lastname': member.family_id.name,
                               'street': member.family_id.street,
                               'street2': member.family_id.street2,
                               'zip': member.family_id.zip,
                               'city': member.family_id.city})

class GolemMember(models.Model):
    """ Member adaptations """
    _inherit = 'golem.member'

    @api.onchange('family_id')
    def onchange_family(self):
        """ Sets lastname as family name if there was no precedence """
        for member in self:
            if not member.lastname:
                member.lastname = member.family_id.name

    @api.multi
    def button_family_members(self):
        """ Go to family view, from member """
        self.ensure_one()
        member = self[0]
        return {'name': _('Family Members'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.family',
                'view_mode': 'form',
                'res_id': member.family_id.id}

    @api.multi
    def create_family(self):
        """ Create family from service user """
        self.ensure_one()
        member = self[0]
        if member.family_id:
            member.family_id = False
        data = {'name': member.lastname,
                'street': member.street,
                'street2': member.street2,
                'zip': member.zip,
                'city': member.city,
                'member_ids': [(4, member.partner_id.id, False)]}
        self.env['golem.family'].create(data)
        # self.family_id = new_family.id

    @api.model
    def create(self, values):
        """ Handles family fields at creation """
        family_id = values.get('family_id')
        if family_id:
            del values['family_id']
        members = super(GolemMember, self).create(values)
        if family_id:
            members.mapped('partner_id').write({'family_id': family_id})
        return members


class GolemFamily(models.Model):
    """ GOLEM Family Entity """
    _name = 'golem.family'
    _description = 'GOLEM Family Entity'
    _inherit = 'mail.thread'

    @api.model
    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    name = fields.Char(index=True, required=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', 'State',
                               ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country',
                                 ondelete='restrict',
                                 default=_get_default_nationality_id)
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    website = fields.Char()

    member_ids = fields.One2many('res.partner', 'family_id', 'Members',
                                 domain=[('is_company', '=', False)])
    single_parent = fields.Boolean()
    note = fields.Text()
    count = fields.Integer(compute='_compute_count', store=True)

    @api.depends('member_ids')
    def _compute_count(self):
        for family in self:
            family.count = len(family.member_ids)

    @api.onchange('member_ids')
    def onchange_members(self):
        """ Sets as member address if there was no precedence """
        for family in self:
            if family.member_ids and not any((family.street, family.street2,\
                                              family.zip, family.city)):
                family.update({'street': family.member_ids[0].street,
                               'street2': family.member_ids[0].street2,
                               'zip': family.member_ids[0].zip,
                               'city': family.member_ids[0].city})

class GolemFamilyRole(models.Model):
    """ GOLEM Family Role """
    _name = 'golem.family.role'
    _description = 'GOLEM Family Role'
    _sql_constraints = [('golem_family_role_name_uniq',
                         'UNIQUE (name)',
                         'Family role must be unique.')]

    name = fields.Char('Role')
