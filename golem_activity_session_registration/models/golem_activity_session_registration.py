# -*- coding: utf-8 -*-

#    copyright 2016 fabien bourgeois <fabien@yaltik.com>
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

from openerp import models, fields


class GolemMember(models.Model):
    _inherit = 'golem.member'

    activity_session_registration_ids = fields.One2many(
        'golem.activity.session.registration', 'member_id', 'Activities')


class GolemActivitySessionRegistration(models.Model):
    _name = 'golem.activity.session.registration'
    _description = 'GOLEM Activity Session Registration'

    member_id = fields.Many2one('golem.member', string='Member', required=True,
                                ondelete='cascade')
    session_id = fields.Many2one('golem.activity.session', required=True,
                                 string='Activity session', ondelete='cascade')
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 ondelete='set null')
    invoice_line_id = fields.Many2one('account.invoice.line',
                                      string='Invoice line',
                                      ondelete='set null')
    season_id = fields.Many2one(string='Season',
                                related='session_id.season_id')
