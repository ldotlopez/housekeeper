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

from . import rcpodcast
from housekeeper import pluginlib


class RadioCastellonPodcastCommand(pluginlib.Command):
    __extension_name__ = 'radiocastellon'

    HELP = 'Generate custom podcast for «Radio Castellón»'
    ARGUMENTS = (
        pluginlib.argument(
            '--data-dir'
        ),
        pluginlib.argument(
            '--podcast-url'
        ),
        pluginlib.argument(
            '--audio-url'
        ),
        pluginlib.argument(
            '--program',
            action='append'
        ),
    )

    def execute(self, app, arguments):
        kwargs_keys = 'data_dir', 'podcast_url', 'audio_url', 'program'

        kwargs = {k: getattr(arguments, k, None) for k in kwargs_keys}
        kwargs['programs'] = kwargs.pop('program')
        kwargs = {k: v for (k, v) in kwargs.items() if v}

        print(repr(kwargs))
        # rcp = rcpodcast.RadioCastellonCustomPodcast(**kwargs)
