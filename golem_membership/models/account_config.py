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

""" Base Account membership configuration for GOLEM """

from odoo import models, api, _


class AccountConfig(models.AbstractModel):
    """ GOLEM Membership Account Configuration """
    _name = 'golem.membership.account.config'
    _description = 'GOLEM Membership Account Configuration'

    @api.model
    def account_settings(self):
        """ Please use better default taxes, account.journal config, base
        accounts for categories """
        account_conf_obj = self.env['account.config.settings']
        data = {'company_id': self.env.ref('base.main_company').id}
        account_conf = account_conf_obj.create(data)
        account_conf.update({
            'default_sale_tax_id': self.env.ref('l10n_fr.tva_0').id,
            'default_purchase_tax_id': self.env.ref('l10n_fr.tva_acq_normale').id
        })
        account_conf.execute()

        journal_obj = self.env['account.journal']
        bank_journal = journal_obj.search([('type', '=', 'bank')], limit=1)
        chk_journal = journal_obj.search([('code', '=', 'CHK')])
        if not chk_journal:
            journal_obj.create({
                'name': _('Check'), 'code': 'CHK', 'type': 'bank',
                'default_debit_account_id': bank_journal.default_debit_account_id.id,
                'default_credit_account_id': bank_journal.default_credit_account_id.id
            })
        ccard_journal = journal_obj.search([('code', '=', 'CCARD')])
        if not ccard_journal:
            journal_obj.create({
                'name': _('Credit Card'), 'code': 'CCARD', 'type': 'bank',
                'default_debit_account_id': bank_journal.default_debit_account_id.id,
                'default_credit_account_id': bank_journal.default_credit_account_id.id
            })

        # Default categories account to 706 and 604
        categories = (self.env.ref('product.product_category_all'),
                      self.env.ref('product.product_category_1'))
        account_obj = self.env['account.account']
        income_account = account_obj.search([('code', '=', '706000')])
        expense_account = account_obj.search([('code', '=', '604000')])
        for categ in categories:
            categ.write({
                'property_account_income_categ_id': income_account.id,
                'property_account_expense_categ_id': expense_account.id
            })
            property_obj = self.env['ir.property']
            income = property_obj.search([('name', '=', 'property_account_income_categ_id')])
            income.write({'value_reference': 'account.account,%s' % income_account.id})
            expense = property_obj.search([('name', '=', 'property_account_expense_categ_id')])
            expense.write({'value_reference': 'account.account,%s' % expense_account.id})
