#!/usr/bin/env python3
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


from os import path
import os
from housekeeper import tools as hktools


nowts = hktools.now()


def archive(src, dst, diff, filter_func=None):
    for (dirpath, dirnames, filenames) in os.walk(src):
        if filter_func:
            filter_func(dirpath, dirnames, filenames)

        for filename in filenames:
            oldpath = dirpath + '/' + filename
            st = os.stat(oldpath)
            stamp = st.st_mtime

            if (stamp + diff) >= nowts:
                continue

            newpath = hktools.pathname_replace(oldpath, src, dst)
            assert oldpath != newpath

            try:
                os.makedirs(path.dirname(newpath))
            except OSError:
                pass

            if not path.exists(newpath):
                print('mv "{}" "{}"'.format(oldpath, newpath))
            else:
                if hktools.same_content(oldpath, newpath):
                    print("rm '{}'".format(oldpath))
                else:
                    print("# unhandled case for '{}' '{}'".format(oldpath, newpath))


def btsyncdir_filter(dirpath, dirnames, filenames):
    try:
        dirnames.remove('.sync')
    except ValueError:
        pass

    hidden = [x for x in filenames if x[0] == '.']
    for x in hidden:
        filenames.remove(x)

if __name__ == '__main__':
    archive(
        path.expanduser('~/Sync/WhatsApp Media'),
        path.expanduser('~/Sync/WhatsApp Media (Archive)'),
        diff=28*24*60*60,
        filter_func=btsyncdir_filter)
