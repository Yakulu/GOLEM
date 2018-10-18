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

""" GOLEM PCS """

from odoo import models, fields, api

class GolemPCS(models.Model):
    """ GOLEM PCS """
    _name = 'golem.pcs'
    _rec_name = 'full_name'
    _order = 'code asc'

    full_name = fields.Char(compute='_compute_full_name', store=True, index=True)
    name = fields.Char(required=True)
    code = fields.Char()
    parent_id = fields.Many2one('golem.pcs', ondelete='cascade')

    @api.depends('name', 'code')
    def _compute_full_name(self):
        """ Computes full name """
        for pcs in self:
            pcs.full_name = u'%s - %s' % (pcs.code, pcs.name) if pcs.code else pcs.name
