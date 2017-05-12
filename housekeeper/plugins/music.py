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


from housekeeper import pluginlib


import copy
import functools
import re


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


class Applet(pluginlib.Command):
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

    def setup_argparser(self, parser):
        # Add subparsers for children
        if self.children:
            chidren_parsers = parser.add_subparsers(dest='child')

            for (name, child) in self.children.items():
                child_parser = chidren_parsers.add_parser(name)
                child.setup_argparser(child_parser)

        for param in self.PARAMETERS:
            fn = parser.add_argument

            if param.short_flag:
                fn = functools.partial(fn, param.short_flag)

            fn = functools.partial(fn, param.long_flag)
            fn(**param.kwargs)

    def execute(self, core, arguments):
        child = arguments.child
        if child and child in self.children:
            return self.children[child].execute(core, arguments)

        parameters = {}
        for param in self.PARAMETERS:
            try:
                parameters[param.name] = getattr(arguments, param.name)
            except AttributeError:
                pass

        return self.main(**parameters)


class MusicPlay(Applet):
    """
    /music/play

    what: What to play (some playlist, artist, album, etc...)
    type: Specify `what` type (optional)
    """
    PARAMETERS = (
        Parameter('what', type=str, required=True),
        Parameter('type', abbr='t', type=str)
    )

    def main(self, **kwargs):
        # Call /usr/bin/media-player play 'what'
        print(repr(kwargs))

    def validator(self, **kwargs):
        # Validate kwargs
        return kwargs


class MusicStop(Applet):
    def main(self, **kwargs):
        # Call /usr/bin/media-player stop
        pass


class MusicPause(Applet):
    def main(self, **kwargs):
        # Call /usr/bin/media-player stop
        pass


class Music(Applet):
    """/music"""
    __extension_name__ = 'music'

    HELP = 'Music control'
    PARAMETERS = (
        Parameter('foo', required=False),
    )

    CHILDREN = (
        ('play', MusicPlay),
        ('pause', MusicPause),
        ('stop', MusicStop),
    )

    def main(self, foo):
        print('Hi! (foo={})'.format(foo))


__housekeeper_extensions__ = [
    Music
]
