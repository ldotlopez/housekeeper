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


from appkit import (
    application,
    loggertools,
    store,
    types
)
from appkit.application import (
    cron,
    commands
)

import abc
import copy
import functools
import os
import re
import yaml


class Parameter:
    def __init__(self, name, abbr=None, **kwargs):
        if not re.match(r'^[a-z0-9-_]+$', name, re.IGNORECASE):
            raise ValueError(name)

        if abbr and len(abbr) != 1:
            msg = "abbr must be a single letter"
            raise ValueError(abbr, msg)

        self.name = str(name).replace('-', '_')
        self.abbr = str(abbr) if abbr else None
        self.kwargs = copy.copy(kwargs)

    @property
    def short_flag(self):
        if not self.abbr:
            return None

        return '-' + self.abbr

    @property
    def long_flag(self):
        return '--' + self.name.replace('_', '-')


class Extension(application.Extension):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = loggertools.getLogger(self.__class__.__extension_name__)
        self.settings = settings


class Applet:
    # FIXME: Rebase Applet onto Extension

    HELP = ""
    CHILDREN = ()
    PARAMETERS = ()

    def __init__(self, *args, **kwargs):
        self.children = {}
        for (name, child_cls) in self.CHILDREN:
            child = child_cls(*args, **kwargs)
            self.children[name] = child

    def main(self, **parameters):
        raise NotImplementedError()


class Callable(Extension):
    @abc.abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def stringify(self, *args, **kwargs):
        raise NotImplementedError()


class Command(commands.Command, Extension):
    pass


class AppletCommandMixin(Command):
    def _applet_setup_argparser(self, applet, parser):
        # Add subparsers for children
        if applet.children:
            chidren_parsers = parser.add_subparsers(dest='child')

            for (name, child) in applet.children.items():
                child_parser = chidren_parsers.add_parser(name)
                self._applet_setup_argparser(child, child_parser)

        for param in applet.PARAMETERS:
            fn = parser.add_argument

            if param.short_flag:
                fn = functools.partial(fn, param.short_flag)

            fn = functools.partial(fn, param.long_flag)
            fn(**param.kwargs)

    def _applet_execute(self, applet, core, arguments):
        child = arguments.child
        if child and child in applet.children:
            return self._applet_execute(applet.children[child], core,
                                        arguments)

        parameters = {}
        for param in applet.PARAMETERS:
            try:
                parameters[param.name] = getattr(arguments, param.name)
            except AttributeError:
                pass

        return applet.main(**parameters)

    def setup_argparser(self, parser):
        self._applet_setup_argparser(self, parser)

    def execute(self, core, arguments):
        return self._applet_execute(self, core, arguments)


class Task(cron.Task, Extension):
    pass


class AppletTaskMixin(Task):
    def execute(self, core):
        self.main()


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


class CronCommand(cron.Command, Command):
    pass


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
