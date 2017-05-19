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


class ItunesBridge(pluginlib.MusicAppBridge):
    __extension_name__ = 'itunes'

    def _osascript(self, s):
        cmd = [
            "osascript",
            "-e",
            "tell application \"iTunes\" to {s}".format(s=s)
        ]
        return subprocess.check_output(cmd)

    def play(self, what=None):
        return self._osascript("play")

    def stop(self):
        return self._osascript("stop")

    def pause(self):
        return self._osascript("pause")


__housekeeper_extensions__ = [
    ItunesBridge
]
