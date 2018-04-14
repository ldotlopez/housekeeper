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


import abc
import collections
import os


import falcon
import yaml
from appkit import (
    application,
    store,
    types
)
from appkit.application import (
    cron,
    commands
)


Parameter = application.Parameter


Command = commands.Command
CommandManager = commands.Manager

Task = cron.Task
CronCommand = cron.Command


class APIEndpoint(application.Extension):
    """
    Expose API functionality.

    Borrowing falcon you should implement:
    - on_get for GET requests
    - on_post for POST request
    etc...
    """
    pass


class AppBridge(application.Extension):
    pass


class MusicBridge(AppBridge):
    Result = collections.namedtuple('Result', ['id', 'name'])

    @abc.abstractproperty
    def state(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def play(self, item=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def pause(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def search(self, query):
        return NotImplementedError


class _APIEndpointMixin:
    METHODS = ['GET']

    def _run_main(self, **params):
        try:
            params = self.validator(**params)
        except NotImplementedError:
            pass

        try:
            return (
                falcon.HTTP_200,
                {
                    'result': self.main(**params)
                }
            )

        except RuntimeError as e:
            return (
                falcon.HTTP_500,
                {
                    'error': e.args[0]
                }
            )

    def on_get(self, req, resp):
        if 'GET' not in self.METHODS:
            resp.status = falcon.HTTP_METHOD_NOT_ALLOWED
            return

        resp.status, resp.context['result'] = self._run_main()

    def on_post(self, req, resp):
        if 'POST' not in self.METHODS:
            resp.status = falcon.HTTP_METHOD_NOT_ALLOWED
            return

        try:
            params = req.context['doc']
        except KeyError:
            resp.status = falcon.HTTP_NOT_ACCEPTABLE
            return

        resp.status, resp.context['result'] = self._run_main(**params)


class _CommandMixin:
    def execute_applet(self, applet, core, arguments):
        try:
            child = arguments.child
        except AttributeError:
            child = []

        if child and child in applet.children:
            return self.execute_applet(applet.children[child], core,
                                       arguments)

        parameters = {}
        for param in applet.PARAMETERS:
            try:
                parameters[param.name] = getattr(arguments, param.name)
            except AttributeError:
                pass

        try:
            parameters = applet.validator(**parameters)
        except NotImplementedError:
            pass

        return applet.main(**parameters)

    def setup_argparser(self, parser):
        if self.children:
            chidren_parsers = parser.add_subparsers(dest='child')
            for (name, child) in self.children.items():
                child_parser = chidren_parsers.add_parser(name)
                child.setup_argparser(child_parser)

        super().setup_argparser(parser)

    def execute(self, core, arguments):
        ret = self.execute_applet(self, core, arguments)

        if ret is None:
            pass

        elif isinstance(ret, str):
            print(ret)

        else:
            print(repr(ret))

        return ret


class Applet(_APIEndpointMixin, APIEndpoint, _CommandMixin, Command):
    HELP = ""
    CHILDREN = ()
    PARAMETERS = ()

    def __init__(self, services, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.srvs = services
        self.children = {}
        self._parent = None

        for (name, child_cls) in self.CHILDREN:
            self.children[name] = self.create_child(name, child_cls, services,
                                                    *args, **kwargs)

    def create_child(self, name, child_cls, *args, **kwargs):
        child = child_cls(*args, **kwargs)
        child._parent = self
        return child

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        root = self.parent
        if not root:
            return self

        while root.parent:
            root = root.parent

        return root

    @abc.abstractmethod
    def main(self, **parameters):
        raise NotImplementedError()

    @abc.abstractmethod
    def validator(self, **parameters):
        raise NotImplementedError()


# class Callable(Extension):
#     @abc.abstractmethod
#     def call(self, *args, **kwargs):
#         raise NotImplementedError()

#     @abc.abstractmethod
#     def stringify(self, *args, **kwargs):
#         raise NotImplementedError()


class CronManager(cron.Manager):
    COMMAND_EXTENSION_CLASS = Command

    def __init__(self, core, state_file, *args, **kwargs):
        super().__init__(core, *args, **kwargs)
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        self.state_file = state_file

    def load_state(self):
        state = store.Store()

        try:
            with open(self.state_file) as fh:
                state.load(fh)

        except FileNotFoundError:
            pass

        return state

    def save_state(self, state):
        with open(self.state_file, 'w+') as fh:
            state.dump(fh)

    def load_checkpoint(self, task):
        store = self.load_state()

        key = 'cron.taskstate.{}'.format(task.__extension_name__)
        ret = store.get(key, default={})

        return ret

    def save_checkpoint(self, task, checkpoint):
        store = self.load_state()

        for (k, v) in checkpoint.items():
            k = 'cron.taskstate.{name}.{key}'.format(
                name=task.__extension_name__,
                key=k)

            store.set(k, v)

        self.save_state(store)


class YAMLStore(store.Store):
    def __init__(self, *args, logger=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not logger:
            logger = types.NullSingleton()

        self.logger = logger

    def dump(self, stream):
        buff = yaml.dump(self.get(None))
        stream.write(buff)

    def load(self, stream):
        buff = stream.read()
        data = yaml.load(buff)
        data = store.flatten_dict(data or {})
        for (k, v) in data.items():
            self.set(k, v)


class RuntimeError(Exception):
    pass
