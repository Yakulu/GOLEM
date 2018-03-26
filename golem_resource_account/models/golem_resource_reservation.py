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
    invoice_line_id = fields.Many2one('account.invoice.line')
    invoice_line_price_subtotal = fields.Monetary(related='invoice_line_id.price_subtotal')
    invoice_id = fields.Many2one(related='invoice_line_id.invoice_id',
                                 string='Invoice')
    invoice_state = fields.Selection(related='invoice_id.state', store=True)
    invoice_amount_total = fields.Monetary(related='invoice_id.amount_total')
    currency_id = fields.Many2one(related='invoice_id.currency_id')

    @api.multi
    def create_invoice(self):
        """ Invoice creation """
        for reservation in self:
            inv_obj = self.env['account.invoice']
            partner_id = reservation.partner_id
            product = reservation.resource_id.product_tmpl_id
            amount = product.list_price

            if not product:
                raise ValidationError(_('You can not create an invoice without '
                                        'linked product on the resource reserved.'))

            account_id = product.property_account_income_id.id or \
                product.categ_id.property_account_income_categ_id.id

            if not account_id:
                raise ValidationError(
                    _('There is no income account defined for this product: "{}"'
                      '. You have to configure it on the product form.'.format(product.name)))

            reservation.invoice_id = inv_obj.create({
                'origin': reservation.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': partner_id.property_account_receivable_id.id,
                'partner_id': partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': reservation.resource_id.name,
                    'origin': reservation.name,
                    'account_id': account_id,
                    'price_unit': amount,
                    'quantity': 1.0,
                    'discount': 0.0,
                    'uom_id': product.uom_id.id,
                    'product_id': product.id,
                    })]
                })
