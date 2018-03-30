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

""" GOLEM Resource Pack Invoicing """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourcePack(models.Model):
    """ GOLEM Resource Pack invoice extention """
    _inherit = 'golem.resource.pack'

    invoice_id = fields.Many2one('account.invoice', string="Invoice")

    invoice_state = fields.Selection(related='invoice_id.state', store=True,
                                     copy=False)
    invoice_amount_total = fields.Monetary(related='invoice_id.amount_total')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    is_products_set = fields.Boolean(compute="compute_is_products_set")

    @api.multi
    def compute_is_products_set(self):
        for pack in self:
            product_list = list(map(lambda x: x.resource_product_id, pack.reservation_ids))
            if len(filter(lambda x: x.id == False, product_list)) > 0:
                pack.is_products_set = False
            else:
                pack.is_products_set = True

    @api.multi
    def create_invoice(self):
        """ Invoice creation """
        for pack in self:
            pack.reservation_ids.check_before_invoicing()
            inv_obj = self.env['account.invoice']
            partner_id = pack.partner_id
            invoice_id = inv_obj.create({
                'origin': pack.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id
            })
            pack.invoice_id = invoice_id.id
            pack.reservation_ids.create_invoice_line(invoice_id)

    @api.multi
    def show_invoice(self):
        """ Redirects to linked invoice """
        self.ensure_one()
        pack = self[0]
        if pack.invoice_id:
            return {'type': 'ir.actions.act_window',
                    'res_model': 'account.invoice',
                    'res_id': pack.invoice_id.id,
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.invoice_form').id}
