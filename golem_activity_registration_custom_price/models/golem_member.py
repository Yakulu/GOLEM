# -*- coding: utf-8 -*-

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

""" GOLEM Member adaptations """

from odoo import models, _

class GolemMember(models.Model):
    """ GOLEM Member adaptations """
    _inherit = 'golem.member'

    def invoice_line_data_get(self, registration):
        """ Overwrite parent method to inject price according to rules """
        line_data = super(GolemMember, self).invoice_line_data_get(registration)
        line_data['pricing_info'] = _(u'Default price')
        member = self[0]
        if member.family_quotient: # default price if no QF
            fq_int = int(member.family_quotient)
            domain = [('family_quotient_from', '<=', fq_int),
                      ('family_quotient_to', '>=', fq_int)]
            rule_slice_id = self.env['golem.payment.rule.familyquotient.slice'].search(
                domain, limit=1
            )
            if rule_slice_id: # if not : default_price
                applicable_areas = []
                area_ids = self.env['golem.partner.area'].search([])
                if member.area_id:
                    applicable_areas += area_ids.filtered(
                        lambda r: r == member.area_id.root_id
                    )
                if not applicable_areas and area_ids:
                    applicable_areas += area_ids[0]
                    random_area = True
                else:
                    random_area = False
                if applicable_areas: # else default_price
                    for applicable_area in applicable_areas:
                        domain = [('activity_id', '=', registration.activity_id.id),
                                  ('area_id', '=', applicable_area.id),
                                  ('slice_id', '=', rule_slice_id.id)]
                        price_line_obj = self.env['golem.activity.price.line']
                        line_id = price_line_obj.search(domain, limit=1)
                        if line_id: # Found !
                            line_data['price'] = line_id.price
                            pricing_info = (_(u'Family quotient but random area')
                                            if random_area else
                                            _(u'Family quotient and area'))
                            line_data['pricing_info'] = pricing_info
                            break
        return line_data
