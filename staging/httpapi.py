from housekeeper import core, kit
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


class API(falcon.API):
    def __init__(self):
        super().__init__(middleware=[
            RequireJSON(),
            JSONTranslator(),
        ])

        self.core = core.Core()
        self.core.register_extension_point(kit.APIEndPoint)
        self.core.load_plugin('aemet')

        for (name, ext) in self.core.get_extensions_for(kit.APIEndPoint):
            route = ext.ROUTE or '/'
            route = '/{name}/{route}'.format(name=name, route=route)
            route = re.subn(r'/+', '/', route)[0]
            print("Map {} to {}".format(route, ext))
            self.add_route(route, ext)


#   http://www.aemet.es/xml/municipios/localidad_12040.xml


app = API()
