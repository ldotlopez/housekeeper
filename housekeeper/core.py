#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import os
import sys

from appkit import (
    application,
    cache,
    loggertools,
    utils
)
from appkit.application import (
    commands,
    services
)
from housekeeper import kit


def user_path(*args, **kwargs):
    kwargs['prog'] = 'housekeeper'
    return utils.user_path(*args, **kwargs)


class Core(services.ApplicationMixin,
           application.BaseApplication):
    def __init__(self):
        # Initialize external modules
        loggertools.setLevel(loggertools.Level.WARNING)

        pluginpath = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
        super().__init__('housekeeper', pluginpath=pluginpath)

        self.commands = commands.Manager(self)
        self.cron = kit.CronManager(
            self,
            state_file=user_path(utils.UserPathType.DATA, 'state.json'))

        self.register_extension_point(kit.Callable)
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

    def get_extension(self, extension_point, name, *args, **kwargs):
        msg = "Calling extension «{}.{}::{}» (args={}, kwargs={})"
        msg = msg.format(
            extension_point.__module__,
            extension_point.__name__,
            name,
            repr(args),
            repr(kwargs))
        self.logger.debug(msg)

        return super().get_extension(extension_point, name, self.settings,
                                     *args, **kwargs)

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
