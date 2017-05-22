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


from housekeeper import kit


import json
import mimetypes
import multiprocessing
import sys
from os import path


import falcon
import gunicorn.app.base


class JSONTranslator(object):
    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in resp.context:
            return

        resp.body = json.dumps(resp.context['result'])


class RequireJSON(object):
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


class APIServer(falcon.API):
    def __init__(self, app, *args, **kwargs):
        middleware = [RequireJSON(), JSONTranslator()]
        super().__init__(*args, middleware=middleware, **kwargs)

        for (name, ext) in app.get_extensions_for(kit.APIEndpoint):
            self.add_extension(name, ext)

    def add_extension(self, name, ext):
        path = '/' + name + '/'
        self.add_route(path, ext)
        print("+ {} {}".format(path, ext))

        for (name_, child) in ext.children.items():
            self.add_extension(name + '/' + name_, child)


class MainResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_303
        resp.location = '/static/index.html'


class StaticSink:
    def __init__(self, *args, prefix='/', **kwargs):
        super().__init__(*args, **kwargs)
        self.root = path.dirname(sys.modules['housekeeper'].__file__)
        self.root = path.dirname(self.root)
        self.prefix = prefix
        self.mime = mimetypes.MimeTypes()

    def on_get(self, req, resp):
        filename = req.path

        if not filename.startswith(self.prefix):
            resp.status = falcon.HTTP_404
            return

        fullpath = self.root + filename
        fullpath = path.realpath(fullpath)
        if not fullpath.startswith(self.root):
            resp.status = falcon.HTTP_404
            return

        mime = self.mime.guess_type(fullpath)[0] or 'application/octet-stream'

        try:
            resp.status = falcon.HTTP_200
            resp.content_type = mime
            with open(fullpath, 'r') as f:
                resp.body = f.read()

        except IOError:
            resp.status = falcon.HTTP_404


class HttpServer(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        sink = StaticSink().on_get

        app.add_route('/', MainResource())
        app.add_sink(sink, prefix='/static/')
        super().__init__()

    def load_config(self):
        config = dict([
            (key, value) for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        ])

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class APIServerCommand(kit.Command):
    __extension_name__ = 'httpapi'
    HELP = 'Start HTTP API server'

    def execute(self, app, arguments):
        options = {
            'bind': '127.0.0.1:8000',
            'graceful_timeout': 0,
            'loglevel': 'debug',
            'proc_name': 'housekeeper-api',
            'reload': True,
            'timeout': 0,
            'workers': 1,  # (multiprocessing.cpu_count() * 2) + 1,
        }
        server = HttpServer(APIServer(app), options)
        server.run()


__housekeeper_extensions__ = [
    APIServerCommand
]