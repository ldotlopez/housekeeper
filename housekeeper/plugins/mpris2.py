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


import contextlib
import os
import sqlite3


import dbus


class MprisMusicBridge(pluginlib.MusicBridge):
    __extension_name__ = 'mpris'
    MPRIS_IMPL = None
    DBUS_MPRIS_NAME_TMPL = 'org.mpris.MediaPlayer2.{impl}'
    DBUS_MPRIS_PATH = '/org/mpris/MediaPlayer2'
    DBUS_MPRIS_INTERFACE_TMPL = 'org.mpris.MediaPlayer2.{interface}'

    @contextlib.contextmanager
    def mpris_interface(self, interface):
        if self.MPRIS_IMPL is None:
            msg = "Implementation name not defined"
            raise TypeError(msg)

        name = self.DBUS_MPRIS_NAME_TMPL.format(impl=self.MPRIS_IMPL)
        interface = self.DBUS_MPRIS_INTERFACE_TMPL.format(
            interface=interface)

        bus = dbus.SessionBus()
        try:
            obj = bus.get_object(name, self.DBUS_MPRIS_PATH)
        except dbus.exceptions.DBusException as e:
            msg = '{msg}'
            msg = msg.format(msg=e.args[0])
            raise pluginlib.RuntimeError(msg) from e

        iface = dbus.Interface(obj, dbus_interface=interface)
        yield iface

    @contextlib.contextmanager
    def player_iface(self):
        with self.mpris_interface('Player') as player:
            yield player

    @contextlib.contextmanager
    def playlists_iface(self):
        with self.mpris_interface('Playlists') as player:
            yield player

    def play(self, item=None):
        if item is None:
            with self.player_iface() as player:
                player.Play()
            return

        with self.playlists_iface() as playlists:
            playlists.ActivatePlaylist(dbus.String(item.id))

    def pause(self):
        with self.player_iface() as player:
            player.Pause()

    def stop(self):
        with self.player_iface() as player:
            player.Stop()

    def search(self, query):
        with self.playlists_iface() as playlists:
            ret = playlists.GetPlaylists(
                    dbus.UInt32(0), dbus.UInt32(100), dbus.String(''),
                    dbus.Boolean(False))

        ret = [pluginlib.MusicBridge.Result(
                    id=str(path),
                    name=str(name)) for (path, name, dummy) in ret]

        return ret


class BansheeMusicBridge(MprisMusicBridge):
    __extension_name__ = 'banshee'
    MPRIS_IMPL = 'banshee'
    DB_PATH = os.path.expanduser('~/.config/banshee-1/banshee.db')
    DBUS_QUEUE_NAME = 'org.bansheeproject.Banshee'
    DBUS_QUEUE_PATH = '/org/bansheeproject/Banshee/SourceManager/PlayQueue'
    DBUS_QUEUE_INTERFACE = 'org.bansheeproject.Banshee.PlayQueue'

    @contextlib.contextmanager
    def db_conn(self):
        yield sqlite3.connect(self.DB_PATH)

    @contextlib.contextmanager
    def queue_iface(self):
        bus = dbus.SessionBus()
        obj = bus.get_object(self.DBUS_QUEUE_NAME, self.DBUS_QUEUE_PATH)
        yield dbus.Interface(obj, dbus_interface=self.DBUS_QUEUE_INTERFACE)

    def play(self, item=None):
        if item is None:
            return super().play()

        type, id = item.id.split(':')
        if type == 'playlist':
            item = pluginlib.MusicBridge.Result(id=id, name=item.name)
            super().play(item)

        rowname = {
            'artist': 'ArtistID',
            'album': 'AlbumId'
        }[type]

        with self.db_conn() as conn:
            res = conn.execute(
                'select Uri from CoreTracks where {}={}'.format(rowname, id)
            )
        tracks = [x[0] for x in res]

        with self.queue_iface() as queue:
            queue.Clear()  # Clear also stops
            for track in tracks:
                queue.EnqueueUri(dbus.String(track), dbus.Boolean(False))

        with self.mpris_interface('Player') as player:
            player.Stop()
            player.Play()

    def search(self, query):
        ret = [
            pluginlib.MusicBridge.Result(
                id='playlist:{}'.format(x.id),
                name=x.name)
            for x in super().search(query)
        ]

        with self.db_conn() as conn:
            res1 = conn.execute(
                'SELECT ArtistID,Name,"artist" from CoreArtists '
                'WHERE Name NOT NULL'
            ).fetchall()
            res2 = conn.execute(
                'SELECT AlbumID,Title,"album" from CoreAlbums '
                'WHERE Title NOT NULL'
            ).fetchall()

        ret.extend([
            pluginlib.MusicBridge.Result(
                id='{}:{}'.format(type, id),
                name=str(name))
            for (id, name, type) in res1 + res2
        ])

        return ret


class ClementineMusicBridge(MprisMusicBridge):
    __extension_name__ = 'clementine'
    MPRIS_IMPL = 'clementine'


__housekeeper_extensions__ = [
    BansheeMusicBridge,
    ClementineMusicBridge
]
