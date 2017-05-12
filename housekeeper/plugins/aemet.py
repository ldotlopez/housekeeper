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


from appkit import application


class AemetAPI:
    def __init__(self, location):
        self.location = location

    @property
    def xml_url(self):
        base = 'http://www.aemet.es/xml/municipios/localidad_{location}.xml'
        return base.format(location=self.location)

    def get(self, key):
        parts = key.split('.')

        if parts[0] == 'rain':
            if parts[1] == 'today':
                pass

            if parts[1] == 'tomorrow':
                pass

        else:
            raise ValueError(key)


class AemetCommand(pluginlib.Command):
    HELP = 'aemet'
    ARGUMENTS = (
        pluginlib.cliargument(
            'when',
            help='keywords')
    )

    def execute(self, app, arguments):
        print(repr(arguments))


__housekeeper_extensions__ = [
    AemetCommand,
]


if __name__ == '__main__':
    application.execute(AemetCommand)
