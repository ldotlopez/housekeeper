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


import subprocess


class ItunesBridge(pluginlib.MusicBridge):
    __extension_name__ = 'itunes'

    def play(self, item=None):
        if not item:
            self.tell('play')
        else:
            self.tell('play the playlist named "{item}"'.format(
                item=item.name))

    def stop(self):
        self.tell('stop')

    def pause(self):
        self.tell('pause')

    def search(self, query):
        pred = """
            repeat with x in (get playlists)
                set n to (name of x)
                log n
            end repeat
        """

        p = self.tell(pred, stderr=subprocess.PIPE)
        lines = p.stderr.decode('utf-8').strip().split('\n')
        ret = [pluginlib.MusicBridge.Result(id=x, name=x)
               for x in lines]

        return ret

    def tell(self, predicate, *args, **kwargs):
        cmd = [
            "osascript",
            "-e",
            """
            tell application "iTunes"
                {predicate}
            end tell
            """.format(predicate=predicate)
        ]
        p = subprocess.run(cmd, *args, **kwargs)
        if p.returncode != 0:
            print(repr(cmd))
            raise ValueError()

        return p


__housekeeper_extensions__ = [
    ItunesBridge
]
