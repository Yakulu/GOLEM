# -*- coding: utf-8 -*-

#    Copyright 2017 Fabien Bourgeois <fabien@yaltik.com>
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

    family_id = fields.Many2one('golem.family', string='Family', index=True)
    family_role = fields.Many2one('golem.family.role', string='Role',
                                  index=True)
    family_count = fields.Integer('Family Count', related='family_id.count')

    @api.multi
    def button_family_members(self):
        """ Go to family view, from partner """
        self.ensure_one()
        return {'name': _('Family Members'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.family',
                'view_mode': 'form',
                'res_id': self.family_id.id}


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


class GolemFamily(models.Model):
    """ GOLEM Family Entity """
    _name = 'golem.family'
    _description = 'GOLEM Family Entity'
    _inherit = 'mail.thread'

    @api.model
    def _get_default_nationality_id(self):
        return self.env.ref('base.main_company').country_id

    name = fields.Char('Name', index=True, required=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State',
                               ondelete='restrict')
    country_id = fields.Many2one('res.country', 'Country',
                                 ondelete='restrict',
                                 default=_get_default_nationality_id)
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    website = fields.Char('Website')

    member_ids = fields.One2many('res.partner', 'family_id', 'Members',
                                 domain=[('is_company', '=', False)])
    note = fields.Text('Note')
    count = fields.Integer('Count', compute='_compute_count', store=True)

    @api.depends('member_ids')
    def _compute_count(self):
        for family in self:
            family.count = len(family.member_ids)


class GolemFamilyRole(models.Model):
    """ GOLEM Family Role """
    _name = 'golem.family.role'
    _description = 'GOLEM Family Role'
    _sql_constraints = [('golem_family_role_name_uniq',
                         'UNIQUE (name)',
                         'Family role must be unique.')]

    name = fields.Char('Role')
