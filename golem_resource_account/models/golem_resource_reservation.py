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

""" GOLEM Resource Reservation  Adaptation"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemResourceReservation(models.Model):
    """ GOLEM Resource Reservation Adaptation """
    _inherit = 'golem.resource.reservation'

    resource_product_id = fields.Many2one(related='resource_id.product_tmpl_id')
    invoice_line_id = fields.Many2one('account.invoice.line', copy=False)
    invoice_line_price_subtotal = fields.Monetary(related='invoice_line_id.price_subtotal')
    invoice_id = fields.Many2one(related='invoice_line_id.invoice_id',
                                 string='Invoice')
    invoice_state = fields.Selection(related='invoice_id.state', store=True,
                                     copy=False)
    invoice_amount_total = fields.Monetary(related='invoice_id.amount_total')
    currency_id = fields.Many2one(related='invoice_id.currency_id')

    @api.multi
    def check_before_invoicing(self):
        """ Checks data coherence before invoicing """
        if len(self.mapped('partner_id')) > 1:
            raise ValidationError(_('You can\'t group reservations of multiple '
                                    'clients in the same invoice, please remove '
                                    'inadequate reservations'))
        for reservation in self:
            if reservation.state != "validated":
                raise ValidationError(
                    _('The reservation "{}" is not validated, please validate '
                      'it before creating invoice'.format(reservation.name)))
            if reservation.invoice_line_id:
                raise ValidationError(_('You can not create an invoice as there '
                                        'is already one.'))
            product = reservation.resource_id.product_tmpl_id

            if not product:
                raise ValidationError(_('You can not create an invoice without '
                                        'linked product on the resource reserved.'))

            account_id = product.property_account_income_id.id or \
                product.categ_id.property_account_income_categ_id.id

            if not account_id:
                raise ValidationError(
                    _('There is no income account defined for this product: "{}"'
                      '. You have to configure it on the product form.'.format(product.name)))

    @api.multi
    def create_invoice_line(self, invoice_id):
        """ Create invoice line corresponding to reservation """
        for reservation in self:
            product = reservation.resource_id.product_tmpl_id
            amount = product.list_price
            account_id = product.property_account_income_id.id or \
                product.categ_id.property_account_income_categ_id.id
            delta = fields.Datetime.from_string(reservation.date_stop) - \
                fields.Datetime.from_string(reservation.date_start)
            quantity = (delta.days * 24) + (delta.seconds/3600.0)

            line_id = self.env['account.invoice.line'].create({
                'invoice_id': invoice_id.id,
                'name': product.name,
                'origin': reservation.name,
                'price_unit': amount,
                'quantity': quantity,
                'uom_id': product.uom_id.id,
                'account_id': account_id,
                'product_id': product.product_variant_id.id,
            })
            reservation.invoice_line_id = line_id

    @api.multi
    def create_invoice(self):
        """ Invoice creation """
        for reservation in self:
            reservation.check_before_invoicing()
            inv_obj = self.env['account.invoice']
            partner_id = reservation.partner_id

            invoice_id = inv_obj.create({
                'origin': reservation.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id
            })
            reservation.create_invoice_line(invoice_id)

    @api.multi
    def show_invoice(self):
        """ Redirects to linked invoice """
        self.ensure_one()
        reservation = self[0]
        if reservation.invoice_id:
            return {'type': 'ir.actions.act_window',
                    'res_model': 'account.invoice',
                    'res_id': reservation.invoice_id.id,
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.invoice_form').id}
    @api.multi
    def add_to_invoice(self):
        """ Add reservation to existing invoice"""
        for reservation in self:
            partner = reservation.partner_id
            invoice_list = self.env['account.invoice'].search([('partner_id', '=', partner.id),
                                                               ('state', '=', 'draft')])
            #test if none
            invoice_ids = invoice_list.mapped('id')
            return {'name' : ("partner's invoice list"),
                    'type' : 'ir.actions.act_window',
                    'res_model' : 'golem.reservation.add.to.invoice.wizard',
                    'context': {'default_invoice_ids': invoice_ids},
                    'view_mode': 'form',
                    'flags': {'initial_mode': 'view'},
                    'target': 'new'}
