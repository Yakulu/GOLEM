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

""" GOLEM Activity Registration Invoicing Wizard """

from odoo import models, api


class GolemActivityRegistrationInvoicing(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Wizard """
    _inherit = 'golem.activity.registration.invoicing'

    @api.depends('member_id')
    def _compute_guardian_ids(self):
        res = super(GolemActivityRegistrationInvoicing, self)._compute_guardian_ids()
        for rec in self:
            if rec.member_id.family_member_ids:
                rec.guardian_ids += rec.member_id.family_member_ids.filtered(
                    lambda r: r.id != self.member_id.partner_id.id
                )
        return res
