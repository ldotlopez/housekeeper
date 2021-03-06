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


from housekeeper import core
from housekeeper import kit


import multiprocessing


import gunicorn.app.base


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class APIServerCommand(kit.Command):
    __extension_name__ = 'httpapi'
    HELP = 'Start HTTP API server'
    PARAMETERS = (
        kit.Parameter('bind', default='127.0.0.1:8000'),
        kit.Parameter('static-folder', default=None),
        kit.Parameter('reload', default=False, action='store_true'),
        kit.Parameter('workers', default=None)
    )

    def execute(self, hk_app, arguments):
        bind = arguments.bind
        reload = bool(arguments.reload)
        static_folder = arguments.static_folder
        if arguments.workers:
            workers = int(arguments.workers)
        else:
            workers = (multiprocessing.cpu_count() * 2) + 1

        options = {
            'bind': bind,
            'graceful_timeout': 0,
            'loglevel': 'debug',
            'proc_name': 'housekeeper-api',
            'reload': reload,
            'timeout': 0,
            'workers': workers
        }

        api_server = core.APIServer(
            hk_app,
            static_folder=static_folder
        )
        server = StandaloneApplication(api_server, options)
        server.run()


__housekeeper_extensions__ = [
    APIServerCommand
]
