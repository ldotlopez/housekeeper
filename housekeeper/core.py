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


from os import path


import collections
import logging
import json
import mimetypes
import os
import sys


import falcon
from appkit import (
    application,
    cache,
    loggertools,
    utils
)
from appkit.application import (
    services
)


def user_path(*args, **kwargs):
    kwargs['prog'] = 'housekeeper'
    return utils.user_path(*args, **kwargs)


CoreServices = collections.namedtuple('CoreServices', [
    'extension_manager',
    'logger',
    'settings',
])


class Core(services.ApplicationMixin, application.BaseApplication):
    def __init__(self):
        # Initialize external modules
        loggertools.setLevel(loggertools.Level.WARNING)

        pluginpath = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
        super().__init__('housekeeper', pluginpath=pluginpath)

        self.commands = kit.CommandManager(self)
        self.cron = kit.CronManager(
            self,
            state_file=user_path(utils.UserPathType.DATA, 'state.json'))

        self.register_extension_point(kit.AppBridge)
        self.register_extension_point(kit.APIEndpoint)
        self.register_extension_class(kit.CronCommand)

        # Read command line
        app_parser = self.commands.build_base_argument_parser()
        app_args, dummy = app_parser.parse_known_args(sys.argv[1:])

        # Read config files
        self.settings = kit.YAMLStore()
        configfiles = [user_path(utils.UserPathType.CONFIG, 'housekeeper.yml')]
        configfiles.extend(getattr(app_args, 'config-files', []))
        for cf in configfiles:
            try:
                with open(cf) as fh:
                    self.settings.load(fh)

            except FileNotFoundError:
                msg = "Config file «{path}» not found"
                msg = msg.format(path=cf)
                self.logger.warning(msg)

        # Apply command line arguments: debug level
        cf_log_level = self.settings.get('log-level', None)
        if cf_log_level:
            try:
                level = getattr(logging.Level, cf_log_level, None)
                logging.setLevel(level)
            except AttributeError:
                msg = "Invalid «log-level={level}» key in settings"
                msg = msg.format(level=cf_log_level)
                self.logger.error(msg)

        level = loggertools.getLevel()
        diff = app_args.verbose - app_args.quiet
        loggertools.setLevel(loggertools.Level.incr(level, n=diff))

        # Initialize cache
        self.cache = cache.DiskCache(
            basedir=user_path(utils.UserPathType.CACHE))

        # Load plugins
        for plugin in app_args.plugins:
            self.load_plugin(plugin)

        for plugin in self.settings.get('plugin', {}):
            key = 'plugin.{}.enabled'.format(plugin)
            if self.settings.get(key, False):
                self.load_plugin(plugin)

    def get_extension(self, extension_point, name, *args, **kwargs):
        msg = "Calling extension «{}.{}::{}» (args={}, kwargs={})"
        msg = msg.format(
            extension_point.__module__,
            extension_point.__name__,
            name,
            repr(args),
            repr(kwargs))
        self.logger.debug(msg)

        cls = self._get_extension_class(extension_point, name)
        if issubclass(cls, kit.Applet):
            services = CoreServices(
                extension_manager=self,
                logger=self.logger.getChild(extension_point.__name__ + '::' +
                                            name),
                settings=self.settings,
            )
            args = (services,) + tuple(args)

        return super().get_extension(extension_point, name, *args, **kwargs)

    def notify(self, summary, body=None, asset=None, actions=None):
        print("*{}*".format(summary))
        if body:
            print(body)

        for (label, callable_, args, kwargs) in actions:
            callable_ = self.get_extension(kit.Callable, callable_)
            print("{label}: {desc}".format(
                label=label,
                desc=callable_.stringify()))

    def execute_from_command_line(self):
        return self.commands.execute_from_command_line()


class APIServer(falcon.API):
    def __init__(self, core, *args, **kwargs):
        middleware = [RequireJSON(), JSONTranslator()]
        super().__init__(*args, middleware=middleware, **kwargs)

        self.registry = {}

        for (name, ext) in core.get_extensions_for(kit.APIEndpoint):
            self.setup_extension(name, ext)

        self.add_route('/', MainResource())
        self.add_route('/_/', IntrospectionResource(self.registry))

        sink = StaticSink().on_get
        self.add_sink(sink, prefix='/static/')

    def setup_extension(self, name, ext):
        path = '/' + name + '/'
        self.add_route(path, ext)
        self.registry[name] = ext
        print("+ {} {}".format(path, ext))

        for (name_, child) in ext.children.items():
            self.setup_extension(name + '/' + name_, child)


class MainResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_303
        resp.location = '/static/index.html'


class IntrospectionResource:
    def __init__(self, reg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reg = reg

    def on_get(self, req, resp):
        resp.context['result'] = {
            name: repr(ext)
            for (name, ext)
            in self.reg.items()
        }


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

        fullpath = path.realpath(self.root + filename)
        if not fullpath.startswith(self.root):
            resp.status = falcon.HTTP_404
            return

        try:
            mime = self.mime.guess_type(fullpath)[0] or 'application/octet-stream'
            resp.status = falcon.HTTP_200
            resp.content_type = mime
            with open(fullpath, 'r') as f:
                resp.body = f.read()

        except IOError:
            resp.status = falcon.HTTP_404


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
