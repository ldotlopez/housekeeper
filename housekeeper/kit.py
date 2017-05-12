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
import os
import yaml


class Extension(application.Extension):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = loggertools.getLogger(self.__class__.__extension_name__)
        self.settings = settings

class Callable(Extension):
    @abc.abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def stringify(self, *args, **kwargs):
        raise NotImplementedError()


class Command(commands.Command, Extension):
    pass


class Task(cron.Task, Extension):
    pass


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
