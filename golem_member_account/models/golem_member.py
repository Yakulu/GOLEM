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

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
_LOGGER = logging.getLogger(__name__)



class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    @api.multi
    def open_partner_invoices(self):
        """ Open invoices member """
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'name': 'Invoices',
                'res_model': 'account.invoice',
                'view_mode': 'tree,form',
                'context': {'search_default_partner_id': self.partner_id.id,
                            'default_partner_id': self.partner_id.id}}


    # state_invoice = fields.One2many(related='member_id.invoice_ids')
    state_last_invoice = fields.Char(compute='_compute_state_of_last_invoice')

    @api.depends('invoice_ids')
    def _compute_state_of_last_invoice(self):
        for member in self:
            if self.invoice_ids.state == 'open':
