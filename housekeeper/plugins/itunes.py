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

    def _osascript(self, s):
        cmd = [
            "osascript",
            "-e",
            "tell application \"iTunes\" to {s}".format(s=s)
        ]
        return subprocess.check_output(cmd)

    def play(self, item=None):
        # osascript -e 'tell application "iTunes" to play'
        if not item:
            self._osascript("play")
        else:
            script = """
            tell application "iTunes"
                play the playlist named "{item}"
            end tell
            """
            cmd = [
                "osascript",
                "-e",
                script.format(item=item.name)
            ]
            subprocess.run(cmd)

    def stop(self):
        # osascript -e 'tell application "iTunes" to stop'
        self._osascript("stop")

    def pause(self):
        # osascript -e 'tell application "iTunes" to pause'
        self._osascript("pause")

    def search(self, query):
        script = """
        tell application "iTunes"
            repeat with x in (get playlists)
                set n to (name of x)
                log n
            end repeat
        end tell
        """

        cmd = [
            "osascript",
            "-e",
            script
        ]

        ret = []
        p = subprocess.run(cmd, stderr=subprocess.PIPE)
        for res in p.stderr.decode('utf-8').strip().split('\n'):
            ret.append(pluginlib.MusicBridge.Result(
                id=res, name=res
            ))

        return ret


__housekeeper_extensions__ = [
    ItunesBridge
]
