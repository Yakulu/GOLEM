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
""" GOLEM Reservation's Adding to invoice wizard"""

from odoo import models, fields, api, _

class GolemReservationAddToInvoiceWizard(models.TransientModel):
    """GOLEM Reservation Add to Invoice Wizard """
    _name = 'golem.reservation.add.to.invoice.wizard'

    invoice_ids = fields.Many2many('account.invoice', string="Partner invoice list")
    reservation_id = fields.Many2one('golem.resource.reservation')

    keyword = fields.Char(required=True)
    member_ids = fields.Many2many('golem.member', string='Members')
    contact_ids = fields.Many2many('res.partner', string='Contacts')

    @api.multi
    def action(self):
        """ Returns action window with current model and instance """
        self.ensure_one()
        return {'name' : _('Search results'),
                'type' : 'ir.actions.act_window',
                'res_model' : self._name,
                'res_id': self[0].id,
                'view_mode': 'form',
                'target': 'new'}

    @api.multi
    def search_partners(self):
        """ Searches partners in name, email """
        self.ensure_one()
        domain = ['|',
                  ('name', 'ilike', self[0].keyword),
                  ('email', 'ilike', self[0].keyword)]
        partner_ids = self.env['res.partner'].search(domain)
        self[0].write({'contact_ids': [(6, False, partner_ids.ids)],
                       'member_ids': [(6, False, partner_ids.mapped('member_id').ids)]})
        return self[0].action()
