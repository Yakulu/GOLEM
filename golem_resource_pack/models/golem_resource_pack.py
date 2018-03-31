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

""" GOLEM Resource Packs """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourcePack(models.Model):
    """ GOLEM Resource Pack Model """
    _name = 'golem.resource.pack'
    _description = 'GOLEM Resource Pack Model'
    _inherit = 'mail.thread'

    name = fields.Char(compute='_compute_name', store=True)
    reservation_ids = fields.One2many('golem.resource.reservation', 'pack_id',
                                      readonly=True, track_visibility='onchange',
                                      states={'draft': [('readonly', False)],
                                              False : [('readonly', False)]})

    note = fields.Text(help='Notes, optional subject for the reservation, reason',
                       track_visibility='onchange',readonly=True,
                       states={'draft': [('readonly', False)],
                               False : [('readonly', False)]})

    user_id = fields.Many2one('res.users', required=True, index=True, readonly=True,
                              string='User', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='On behalf of', required=True,
                                 index=True, track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)],
                                         False : [('readonly', False)]})
    state = fields.Selection([('canceled', 'Canceled'),
                              ('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('validated', 'Validated'),
                              ('rejected', 'Rejected')],
                             default='draft', compute="_compute_pack_state",
                             track_visibility='onchange')
    reservation_count = fields.Integer(compute="_compute_reservation_count",
                                       string="Reservation count")
    rejection_reason = fields.Text(readonly=True, track_visibility='onchange')

    @api.multi
    @api.constrains('partner_id')
    def set_reservation_partner(self):
        for pack in self:
            pack.reservation_ids.write({'partner_id': pack.partner_id.id})

    @api.multi
    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for pack in self:
            pack.reservation_count = len(pack.reservation_ids)

    @api.multi
    def state_confirm(self):
        """ pack confirm """
        for pack in self:
            pack.reservation_ids.state_confirm()

    @api.multi
    def state_draft(self):
        """ pack canceled """
        for pack in self:
            pack.reservation_ids.state_draft()

    @api.multi
    def state_canceled(self):
        """ pack canceled """
        for pack in self:
            pack.reservation_ids.state_canceled()

    @api.multi
    def state_validated(self):
        """ pack validated """
        for pack in self:
            pack.reservation_ids.state_validated()

    @api.multi
    def state_rejected(self):
        """ Wizard call for pack reject """
        self.ensure_one()
        pack_id = self[0]
        return {'name' : _('Please enter the rejection reason'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'golem.pack.rejection.wizard',
                'context': {'default_pack_id': pack_id.id},
                'view_mode': 'form',
                'target': 'new'}


    @api.depends('partner_id')
    def _compute_name(self):
        """ Compute pack name """
        for pack in self:
            pack.name = u'{}/{}'.format(pack.partner_id.name,
                                        pack.create_date)
    @api.multi
    @api.constrains('reservation_ids')
    def check_reservation_partner(self):
        for pack in self:
            if len(filter(lambda x: x.partner_id == pack.partner_id, pack.reservation_ids)) < len(pack.reservation_ids):
                raise ValidationError(_('Pack client should be the same for all reservations'))

    @api.multi
    @api.depends('reservation_ids')
    def _compute_pack_state(self):
        """ get pack state """
        for pack in self:
            reservation_states = list(map(lambda x: x.state, pack.reservation_ids))
            if "rejected" in reservation_states:
                pack.state = 'rejected'
            elif "canceled" in reservation_states:
                pack.state = 'canceled'
            elif "draft" in reservation_states:
                pack.state = 'draft'
            elif "confirmed" in reservation_states:
                pack.state = 'confirmed'
            elif "validated" in reservation_states:
                pack.state = 'validated'
