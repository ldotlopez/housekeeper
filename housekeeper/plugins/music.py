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
        pluginlib.Parameter('what', type=str, required=False),
        pluginlib.Parameter('type', abbr='t', type=str)
    )

    def main(self, what, type):

        if what is None:
            return self.root.appbridge.play()

        results = self.root.appbridge.search(what)
        if not results:
            raise ValueError()

        selection = results[0]
        self.root.appbridge.play(selection['id'], type=selection['type'])

    def validator(self, **kwargs):
        # Validate kwargs
        return kwargs


class MusicStop(pluginlib.Applet):
    def main(self, **kwargs):
        return self.root.appbridge.stop()


class MusicPause(pluginlib.Applet):
    def main(self, **kwargs):
        return self.root.appbridge.pause()


class MusicSearch(pluginlib.Applet):
    PARAMETERS = (
        pluginlib.Parameter('query', required=False),
    )

    def main(self, query=None):
        ret = []

        playlists = self.root.appbridge.query(query)
        ret.extend([('playlist', x[0], x[1]) for x in playlists])

        return ret


class Music(pluginlib.Applet):
    SETTINGS_NS = 'plugin.music.'
    HELP = 'Music control'
    PARAMETERS = (
        pluginlib.Parameter('foo', required=False),
    )

    CHILDREN = (
        ('play', MusicPlay),
        ('pause', MusicPause),
        ('stop', MusicStop),
        ('search', MusicSearch),
    )

    def __init__(self, *args, **kwargs):
        # Link to music player
        # appbridge_settings = services.settings.get('music')
        # self.appbridge = MusicAppBridge(**appbridge_settings)
        super().__init__(*args, **kwargs)
        bridge = self.srvs.settings.get(self.SETTINGS_NS + 'bridge')
        self.appbridge = self.srvs.extension_manager.get_extension(
            pluginlib.AppBridge, bridge)

    def main(self, foo=None):
        return 'Hi! (foo={})'.format(foo)


class MusicApplet(Music):
    __extension_name__ = 'music'


__housekeeper_extensions__ = [
    MusicApplet
]
