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

""" Pre-migration script """

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=False)
def migrate(cursor, version):
    """ Keep old columns in database for migration """
    cursor.execute('ALTER TABLE golem_resource RENAME COLUMN avaibility_start TO availability_start')
    cursor.execute('ALTER TABLE golem_resource RENAME COLUMN avaibility_stop TO availability_stop')
    cursor.execute('ALTER TABLE golem_resource RENAME COLUMN availibility_24_7 TO availability_24_7')
    cursor.execute('ALTER TABLE golem_resource_timetable RENAME COLUMN availibility_24 TO availability_24')
