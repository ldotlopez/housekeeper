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


from difflib import SequenceMatcher


import dbus


class MprisMusicBridge(pluginlib.MusicBridge):
    __extension_name__ = 'mpris'
    IMPL = None

    def __init__(self, *args, **kwargs):
        if self.IMPL is None:
            msg = "Implementation name not defined"
            raise TypeError(msg)

        super().__init__(*args, **kwargs)
        bus = dbus.SessionBus()

        for name in bus.list_names():
            if name == 'org.mpris.MediaPlayer2.' + self.IMPL:
                break
        else:
            msg = "player not found"
            raise ValueError(msg)

        player_obj = bus.get_object(name, '/org/mpris/MediaPlayer2')
        self.player = dbus.Interface(player_obj, dbus_interface='org.mpris.MediaPlayer2.Player')
        self.playlists = dbus.Interface(player_obj, dbus_interface='org.mpris.MediaPlayer2.Playlists')

    def play(self, what=None, type=None):
        if what is None:
            self.player.Play()
            return

        if type != 'playlist':
            raise NotImplementedError()

        self.playlists.ActivatePlaylist(dbus.String(what))

    def pause(self):
        self.player.Pause()

    def stop(self):
        self.player.Stop()

    def search(self, query):
        def distance(a, b):
            return SequenceMatcher(None, a, b).ratio()

        ret = []

        playlists = self.get_playlists()
        for path, name in playlists:
            dist = distance(name, query)
            if dist < 0.3:
                continue

            ret.append({
                'q': dist,
                'id': str(path),
                'type': 'playlist',
                'name':str(name)
            })

        return list(sorted(ret, key=lambda x: x['q'], reverse=True))

    def get_playlists(self):
        playlists = self.playlists.GetPlaylists(
            dbus.UInt32(0), dbus.UInt32(100), dbus.String(''),
            dbus.Boolean(False))

        return [(x[0], x[1]) for x in playlists]


class BansheeMusicBridge(MprisMusicBridge):
    __extension_name__ = 'banshee'
    IMPL = 'banshee'


__housekeeper_extensions__ = [
    BansheeMusicBridge
]
