# -*- coding: utf-8 -*-

#    Copyright 2018 Youssef El Ouahby <youssef@yaltik.com>
#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Legal Guardian Management """

from odoo import models, fields, _

class GolemLegalGuardian(models.Model):
    """ GOLEM Legal Guardian Management """
    _name = 'golem.legal.guardian'
    _description = 'GOLEM Legal Guardian Management'
    _sql_constraints = [(
        'golem_legal_guardian_uniq', 'UNIQUE (member_id, legal_guardian_id)',
        _('There are doubles in your legal guardians. Please check your fills.')
    )]

    member_id = fields.Many2one('golem.member', required=True,
                                index=True, auto_join=True,
                                ondelete='cascade')
    legal_guardian_id = fields.Many2one(
        'res.partner', required=True, index=True, auto_join=True,
        string='Legal guardian', ondelete='cascade',
        domain="[('is_company', '=', False)]"
    )
    contact_address = fields.Char(related='legal_guardian_id.contact_address')
    phone = fields.Char(related='legal_guardian_id.phone')
    mobile = fields.Char(related='legal_guardian_id.mobile')
    email = fields.Char(related='legal_guardian_id.email')
    is_default_guardian = fields.Boolean()
