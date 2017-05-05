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


import json
from os import path

from appkit import application


class DropboxService(application.Service):
    __extension_name__ = 'dropbox'

    def __init__(self, app):
        super().__init__(app)

        try:
            with open(path.expanduser('~/.dropbox/info.json')) as fh:
                conf = json.loads(fh.read())

        except IOError:
            print("No dropbox path")

        self._db_dirs = [conf[x]['path'] for x in conf]

    @property
    def dirs(self):
        return self._db_dirs


class DropboxCommand(application.Command):
    __extension_name__ = 'dropbox'

    HELP = 'Dropbox tools'
    ARGUMENTS = ()

    def run(self, application, args):
        srv = application.get_service('dropbox')
        print(repr(srv.dirs))


__housekeeper_extensions__ = [
    DropboxCommand,
    DropboxService
]
