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


class GolemMember(models.Model):
    _inherit = 'golem.member'

    family_count = fields.Integer('Family', compute='_compute_family_count')

    @api.one
    def _compute_family_count(self):
        pid = self.partner_id.id
        dmn = ['|', ('partnerfrom_id', '=', pid), ('partnerto_id', '=', pid)]
        self.family_count = self.env['golem.member.family'].search_count(dmn)

    @api.multi
    def button_family_members(self):
        self.ensure_one()
        pid = self.partner_id.id
        return {'name': _('Family Members'),
                'type': 'ir.actions.act_window',
                'res_model': 'golem.member.family',
                'view_mode': 'tree',
                'context': {'default_partnerfrom_id': pid},
                'domain': ['|',
                           ('partnerfrom_id', '=', pid),
                           ('partnerto_id', '=', pid)]}


class GolemFamily(models.Model):
    _name = 'golem.member.family'
    _description = 'GOLEM Member Family'

    partnerfrom_id = fields.Many2one('res.partner', 'Family member from',
                                     required=True, index=True,
                                     domain=[('is_company', '=', False)])
    partnerto_id = fields.Many2one('res.partner', 'Family member to',
                                   required=True, index=True,
                                   domain=[('is_company', '=', False)])
    relation_id = fields.Many2one('golem.member.family.relation',
                                  required=True, index=True,
                                  string='Family relation')
    fullrelation = fields.Char('Full relation string',
                               compute='_compute_fullrelation', store=True)

    @api.depends('partnerfrom_id', 'partnerto_id', 'relation_id')
    def _compute_fullrelation(self):
        for r in self:
            r.fullrelation = '{} -> {} -> {}'.format(r.partnerfrom_id.name,
                                                     r.relation_id.name,
                                                     r.partnerto_id.name)

    @api.onchange('partnerfrom_id')
    def onchange_partnerfrom_id(self):
        """ If tree from member, use ctx default partner to populate from """
        default_pid = self.env.context.get('default_partnerfrom_id')
        if default_pid:
            self.partnerfrom_id = default_pid


class GolemFamilyRelation(models.Model):
    _name = 'golem.member.family.relation'
    _description = 'GOLEM Member Family Relation'
    _sql_constraints = [('golem_member_family_relation_name_uniq',
                         'UNIQUE (name)',
                         'Family relation must be unique.')]

    name = fields.Char('Relation')
