# -*- coding: utf-8 -*-

#    Copyright 2017-2018 Fabien Bourgeois <fabien@yaltik.com>
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

""" Golem Legal Gardian Management """

from odoo import models, fields, api

class GolemLegalGardian(models.Model):
    """ Golem Legal Gardian Management """
    _name = 'golem.legal.gardian'

    member_id = fields.Many2one('golem.member', required=True,
                                ondelete='cascade',
                                readonly=True)
    legal_gardian_id = fields.Many2one('res.partner', required=True,
                                       domain="[('is_company', '=', False)]",
                                       ondelete='cascade')
    name = fields.Char(related="legal_gardian_id.name")
    contact_address = fields.Char(related="legal_gardian_id.contact_address")
    phone = fields.Char(related="legal_gardian_id.phone")
    mobile = fields.Char(related="legal_gardian_id.mobile")
    email = fields.Char(related="legal_gardian_id.email")


    is_default_gardian = fields.Boolean()


    def do_default_gardian(self):
        """ Make current only default gardian """
        self.ensure_one()
        self.write({'is_default_gardian': True})
        legal_list = self.member_id.legal_guardian2_ids.filtered(
            lambda a: a.legal_gardian_id not in self.legal_gardian_id)
        legal_list.write({'is_default_gardian': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
            }

    @api.model
    def create(self, values):
        """ If current gardian is default if the only, and the only if default """
        if values['is_default_gardian']:
            self.env['golem.member'].browse(values['member_id']).legal_guardian2_ids.write(
                {'is_default_gardian': False})
        if not self.env['golem.member'].browse(values['member_id']).legal_guardian2_ids:
            values['is_default_gardian'] = True
        return  super(GolemLegalGardian, self).create(values)
