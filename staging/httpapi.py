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


from housekeeper import core, kit
from housekeeper.lib import hkfilesystem
import falcon
import re
import json


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


class Adapter:
    def __init__(self, applet):
        self.applet = applet

    def on_get(self, req, resp):
        try:
            resp.context['result'] = {
                'result': self.applet.main(**req.params)
            }
            resp.status = falcon.HTTP_200

        except SyntaxError:
            raise

        except Exception as e:
            resp.context['result'] = {
                'error': str(e)
            }
            resp.status = falcon.HTTP_500


class API(falcon.API):
    def __init__(self):
        super().__init__(middleware=[
            RequireJSON(),
            JSONTranslator(),
        ])

        self.core = core.Core()
        self.core.register_extension_point(kit.APIEndpoint)
        self.core.load_plugin('music')
        for (name, ext) in self.core.get_extensions_for(kit.APIEndpoint):
            if not isinstance(ext, kit.Applet):
                continue

            self.add_applet(name, ext)
            print(name, ext)

    def add_applet(self, name, applet):
        path = '/' + name + '/'
        self.add_route(path, Adapter(applet))

        for (name_, child) in applet.children.items():
            self.add_applet(name + '/' + name_, child)

app = API()
