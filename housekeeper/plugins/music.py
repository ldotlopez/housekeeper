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


import difflib


class MusicPlay(pluginlib.Applet):
    """
    what: What to play (some playlist, artist, album, etc...)
    """

    PARAMETERS = (
        pluginlib.Parameter('what', type=str, required=False),
    )

    def main(self, what):
        if what:
            lc_what = what.lower()

        def distance(x):
            return difflib.SequenceMatcher(None, lc_what, x.lower()).ratio()

        # Just play
        if what is None:
            return self.root.appbridge.play()

        results = self.root.appbridge.search(what)
        if not results:
            raise ValueError()

        results = list(sorted(results, key=lambda x: distance(x.name), reverse=True))
        self.root.appbridge.play(results[0])

    def validator(self, **kwargs):
        params = {
            'what': kwargs.get('what', None) or None
        }

        return params


class MusicStop(pluginlib.Applet):
    def main(self, **kwargs):
        return self.root.appbridge.stop()


class MusicPause(pluginlib.Applet):
    def main(self, **kwargs):
        return self.root.appbridge.pause()


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
    )

    def __init__(self, *args, **kwargs):
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
