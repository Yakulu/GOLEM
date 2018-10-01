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

""" Golem Legal Guardian Management """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GolemLegalGuardian(models.Model):
    """ Golem Legal Guardian Management """
    _name = 'golem.legal.guardian'

    member_id = fields.Many2one('golem.member', required=True,
                                ondelete='cascade',
                                readonly=True)
    legal_guardian_id = fields.Many2one('res.partner', required=True,
                                        domain="[('is_company', '=', False)]",
                                        ondelete='cascade')
    name = fields.Char(related="legal_guardian_id.name")
    contact_address = fields.Char(related="legal_guardian_id.contact_address")
    phone = fields.Char(related="legal_guardian_id.phone")
    mobile = fields.Char(related="legal_guardian_id.mobile")
    email = fields.Char(related="legal_guardian_id.email")


    is_default_guardian = fields.Boolean()

    def do_default_guardian(self):
        """ Make current only default guardian """
        self.ensure_one()
        self.write({'is_default_guardian': True})
        legal_list = self.member_id.legal_guardian_ids.filtered(
            lambda a: a.legal_guardian_id not in self.legal_guardian_id)
        legal_list.write({'is_default_guardian': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
            }

    @api.model
    def create(self, values):
        """ Make the current guardian is default if the only, and the only if default """
        if values['is_default_guardian']:
            self.env['golem.member'].browse(values['member_id']).legal_guardian_ids.write(
                {'is_default_guardian': False})
        if not self.env['golem.member'].browse(values['member_id']).legal_guardian_ids:
            values['is_default_guardian'] = True
        return  super(GolemLegalGuardian, self).create(values)

    @api.multi
    def unlink(self):
        """ Forbids default legal guardian removal """
        for guardian in self:
            if guardian.is_default_guardian and len(guardian.member_id.legal_guardian_ids) > 1:
                emsg = _('You can\'t delete the default legal guardian')
                raise ValidationError(emsg)
            else:
                return super(GolemLegalGuardian, self).unlink()
