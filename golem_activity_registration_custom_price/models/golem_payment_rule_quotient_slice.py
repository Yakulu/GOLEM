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

""" GOLEM Payment Rule Family Quotient Slice """

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GolemPaymentRuleQuotientSlice(models.Model):
    """ GOLEM Payment Rule Family Quotient Slice """
    _name = 'golem.payment.rule.familyquotient.slice'
    _description = 'GOLEM Payment Rule Family Quotient Slice'
    _order = 'name asc'
    _sql_constraints = [(
        'golem_payment_rule_fquoslice_uniq', 'UNIQUE (name)',
        _('This name has already been used. It must be unique.')
    )]

    name = fields.Char(required=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    family_quotient_from = fields.Monetary()
    family_quotient_to = fields.Monetary()

    @api.constrains('family_quotient_from', 'family_quotient_to')
    def check_fq(self):
        """ Check family quotient coherence and conflits """
        for rqf in self:
            if rqf.family_quotient_from:
                if (not rqf.family_quotient_to or
                        rqf.family_quotient_to < rqf.family_quotient_from):
                    verr = _('The \'to\' family quotient must be higher than '
                             'the \'from\' one.')
                    raise ValidationError(verr)
                rqfs = self.env['golem.payment.rule.familyquotient.slice'].search([])
                for eachr in rqfs:
                    if (eachr.family_quotient_from < rqf.family_quotient_from <
                            eachr.family_quotient_to):
                        verr = _(u'Family quotient from is in range of an '
                                 'existing slice.')
                        raise ValidationError(verr)
                    if (eachr.family_quotient_from < rqf.family_quotient_to <
                            eachr.family_quotient_to):
                        verr = _(u'Family quotient to is in range of an '
                                 'existing slice.')
                        raise ValidationError(verr)
                    if (rqf.family_quotient_from < eachr.family_quotient_from <
                            rqf.family_quotient_to):
                        verr = _(u'Current family quotient slice cannot be '
                                 'included into another existing slice.')
                        raise ValidationError(verr)
