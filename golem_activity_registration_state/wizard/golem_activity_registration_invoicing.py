# -*- coding: utf-8 -*-

#    copyright 2017 fabien bourgeois <fabien@yaltik.com>
#
#    this program is free software: you can redistribute it and/or modify
#    it under the terms of the gnu affero general public license as
#    published by the free software foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    this program is distributed in the hope that it will be useful,
#    but without any warranty; without even the implied warranty of
#    merchantability or fitness for a particular purpose.  see the
#    gnu affero general public license for more details.
#
#    you should have received a copy of the gnu affero general public license
#    along with this program.  if not, see <http://www.gnu.org/licenses/>.

""" GOLEM Activity Registration Invoicing Wizard """

from odoo import models, fields, api

class GolemActivityRegistrationInvoicingLine(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Lines """
    _name = 'golem.activity.registration.invoicing.line'
    description = 'GOLEM Activity Registration Invoicing Lines'

    invoicing_id = fields.Many2one('golem.activity.registration.invoicing',
                                   required=True)
    activity_id = fields.Many2one('golem.activity', required=True, readonly=True)
    price = fields.Float('Price')

class GolemActivityRegistrationInvoicing(models.TransientModel):
    """ GOLEM Activity Registration Invoicing Wizard """
    _name = 'golem.activity.registration.invoicing'
    _description = 'GOLEM Activity Registration Invoicing Wizard'

    season_id = fields.Many2one('golem.season', 'Season', required=True)
    member_id = fields.Many2one('golem.member', 'Member', required=True)
    line_ids = fields.One2many('golem.activity.registration.invoicing.line',
                               'invoicing_id', string='Activities')
    schedule_id = fields.Many2one('golem.payment.schedule', 'Payment schedule',
                                  domain='[("season_id", "=", season_id)]',
                                  help='If no schedule is selected, only the '
                                  'invoice will be create. Otherwise, draft '
                                  'payments will be generated.')

    @api.multi
    def validate(self):
        """ Validate and create invoice and payments """
        self.ensure_one()
        draft_registrations = self.member_id.activity_registration_ids.filtered(
            lambda r: r.state == 'draft')
        draft_registrations.write({'state': 'confirmed'})
