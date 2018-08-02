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

""" GOLEM Resource Reservation testing """

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
_LOGGER = logging.getLogger(__name__)


class TestGolemResourcePack(TransactionCase):
    """ GOLEM Resource Pack testing """

    def setUp(self, *args, **kwargs):
        """ Bootstrap Resource Reservation """
        super(TestGolemResourcePack, self).setUp(*args, **kwargs)
        # set product
        self.product = self.env['product.template'].create({
            'name': 'Product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'list_price': 7.0,
            'type': 'service',
            'uom_id': self.env.ref('product.product_uom_hour').id,
            'uom_po_id': self.env.ref('product.product_uom_hour').id,
            'property_account_income_id': self.env.ref('l10n_fr.pcg_706').id
        })
        #set resources
        self.resource_1 = self.env['golem.resource'].create({
            'name': 'Resource1',
            'product_tmpl_id': self.product.id,
            'availability_start': '2018-01-01',
            'availability_stop': '2020-01-01',
            'availability_24_7': True
        })
        self.resource_2 = self.env['golem.resource'].create({
            'name': 'Resource2',
            'availability_start': '2018-01-01',
            'availability_stop': '2020-01-01',
            'availability_24_7': True
        })

        #set partners
        self.partner_1 = self.env['res.partner'].create({'firstname': 'John',
                                                         'lastname': 'DOE',
                                                         'is_company': False})
        self.partner_2 = self.env['res.partner'].create({'firstname': 'John2',
                                                         'lastname': 'DOE2',
                                                         'is_company': False})

        # set reservations
        self.reservation_1 = self.env['golem.resource.reservation'].create({
            'resource_id': self.resource_1.id,
            'date_start': '2018-02-05 11:00:00',
            'date_stop': '2018-02-05 12:00:00',
            'partner_id': self.partner_1.id
        })
        self.reservation_2 = self.env['golem.resource.reservation'].create({
            'resource_id': self.resource_1.id,
            'date_start': '2018-02-06 11:00:00',
            'date_stop': '2018-02-06 12:00:00',
            'partner_id': self.partner_1.id
        })

        #set pack env
        self.pack_obj = self.env['golem.resource.pack']
        self.pack_data = {
            'name': 'Pack test',
            'partner_id': self.partner_1.id,
            'reservation_ids': [(4, self.reservation_1.id, 0),
                                (4, self.reservation_2.id, 0)]}


    def test_pack_invoice_basic(self):
        """ Test pack invoice basic """
        pack = self.pack_obj.create(self.pack_data)
        pack.state_confirm()
        pack.create_invoice()
        self.assertTrue(pack.invoice_id.id)
        self.assertEqual(pack.invoice_state, 'draft')

    def test_unallowed_pack_invoice(self):
        """ Test unallowed pack invoice cases """
        pack = self.pack_obj.create(self.pack_data)
        with self.assertRaises(ValidationError) as err:
            pack.create_invoice()
        self.assertIn(u'current pack is not validated', err.exception.args[0])
        self.reservation_2.write({'resource_id': self.resource_2.id})#no product linked
        pack.state_confirm()
        with self.assertRaises(ValidationError) as err:
            pack.create_invoice()
        self.assertIn(u'linked product on every resource', err.exception.args[0])
        pack.state_draft()
        self.reservation_2.write({'resource_id': self.resource_1.id})# with product linked
        pack.state_confirm()
        pack.create_invoice()
        self.assertTrue(pack.invoice_id.id)
        with self.assertRaises(ValidationError) as err:
            pack.create_invoice()
        self.assertIn(u'can not create an invoice as there', err.exception.args[0])
