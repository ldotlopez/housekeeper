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
