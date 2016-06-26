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

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_ids = fields.Many2many('golem.member.family',
                                  string='Family member')

    # @api.multi
    # def button_family_members(self):
    #     self.ensure_one()
    #     return {'name': _('Family Members'),
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'golem.member.family',
    #             'view_mode': 'tree',
    #             'domain': [('memberfrom_id', '=', self[0].id)]}


class GolemFamily(models.Model):
    _name = 'golem.member.family'
    _description = 'GOLEM Member Family'

    memberfrom_id = fields.Many2one('golem.member', 'Family member 1')
    memberto_id = fields.Many2one('golem.member', string='Family member 2')
    relation_id = fields.Many2one('golem.member.family.relation',
                                  string='Family relation')

    # @api.onchange('member_id')
    # def onchange_member_id(self):
    #     mid = self.env.context.get('default_member_id')
    #     member = self.env['golem.member'].browse([mid])
    #     self.member_id = member.partner_id.id
    #     return self


class GolemFamilyRelation(models.Model):
    _name = 'golem.member.family.relation'
    _description = 'GOLEM Member Family Relation'
    _sql_constraints = [('golem_member_family_relation_name_uniq',
                         'UNIQUE (name)',
                         'Family relation must be unique.')]

    name = fields.Char('Relation')
