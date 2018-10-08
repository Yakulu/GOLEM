# -*- coding: utf-8 -*-

#    Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" GOLEM Membership """

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class GolemMembershipInvoice(models.TransientModel):
    """ Membership invoicing """
    _inherit = 'golem.membership.invoice'


    src_member_id = fields.Many2one('golem.member')
    partner_id = fields.Many2one(required=True)

    @api.onchange('src_member_id')
    def onchange_member(self):
        """ Set partner domain if src_member_id is filled """
        record = self[0]
        if record.src_member_id.is_minor:
            return {'domain': {'partner_id':
                               [('id', 'in', record.src_member_id.legal_guardian_ids.ids)]
                              }
                   }
