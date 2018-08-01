# -*- coding: utf-8 -*-

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

""" GOLEM Activity Registration adaptations """

from odoo import models, fields

class GolemActivityRegistration(models.Model):
    """ GOLEM Activity Registration adaptations """
    _inherit = 'golem.activity.registration'

    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice line',
                                      ondelete='set null')
    invoice_id = fields.Many2one(related='invoice_line_id.invoice_id')
    invoice_state = fields.Selection(related='invoice_line_id.invoice_id.state',
                                     store=True)
