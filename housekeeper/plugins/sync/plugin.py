# -*- coding: utf-8 -*-

# Copyright (C) 2015 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


from housekeeper import pluginlib
from housekeeper import tools
from housekeeper.plugins.sync import sync


class Task(pluginlib.Task):
    __extension_name__ = 'sync'
    INTERVAL = '0'

    def __init__(self, settings):
        super().__init__(settings)

        # Parse options
        self.api = sync.SyncAPI(
            exclude=settings.get('plugins.sync.exclude', default=[])
        )

    def get_syncs(self):
        syncs = self.settings.get('syncs', default=[])

        for (id_, opts) in tools.walk_collection(syncs):
            genname = opts.pop('generator')
            genopts = {}

            if isinstance(genname, dict):
                genname, genopts = genname.pop('name'), genname

            gen = sync.generator_factory(genname, **genopts)
            try:
                tools.validate_mapping(opts,
                                       required=['source', 'destination'],
                                       optional=['hardlink', 'exclude'])
            except tools.MappingValidationError as e:
                print(repr(e))
                continue

            yield sync.SyncOperation(generator=gen, **opts)

    def execute(self, app):
        for op in self.get_syncs():
            self.api.sync(op)
