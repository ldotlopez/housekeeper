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


class MusicPlay(pluginlib.Applet):
    """
    /music/play

    what: What to play (some playlist, artist, album, etc...)
    type: Specify `what` type (optional)
    """
    PARAMETERS = (
        pluginlib.Parameter('what', type=str, required=True),
        pluginlib.Parameter('type', abbr='t', type=str)
    )

    def main(self, **kwargs):
        # Call /usr/bin/media-player play 'what'
        return {v: k for (k, v) in kwargs.items()}

    def validator(self, **kwargs):
        # Validate kwargs
        return kwargs


class MusicStop(pluginlib.Applet):
    def main(self, **kwargs):
        # Call /usr/bin/media-player stop
        pass


class MusicPause(pluginlib.Applet):
    def main(self, **kwargs):
        # Call /usr/bin/media-player stop
        pass


class Music(pluginlib.Applet):
    HELP = 'Music control'
    PARAMETERS = (
        pluginlib.Parameter('foo', required=False),
    )

    CHILDREN = (
        ('play', MusicPlay),
        ('pause', MusicPause),
        ('stop', MusicStop),
    )

    def __init__(self, *args, **kwargs):
        # Link to music player
        # appbridge_settings = services.settings.get('music')
        # self.appbridge = MusicAppBridge(**appbridge_settings)
        super().__init__(*args, **kwargs)
        self.appbridge = object()

    def main(self, foo=None):
        return 'Hi! (foo={})'.format(foo)


class MusicApplet(Music):
    __extension_name__ = 'music'


__housekeeper_extensions__ = [
    MusicApplet
]
