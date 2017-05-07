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


import os
import shutil
from urllib import parse

from appkit import utils


import humanfriendly
from . import (
    hkdigest,
    hkdatatools
)


class Operations:
    NONE = 0
    MOVE = 1
    UNLINK = 2


def archive(src, dst, diff, filter_func=None, dry_run=False):
    nowts = utils.now_timestamp()
    ret = []

    for (dirpath, dirnames, filenames) in os.walk(src):
        if filter_func:
            filter_func(dirpath, dirnames, filenames)

        for filename in filenames:
            oldpath = dirpath + '/' + filename
            st = os.stat(oldpath)
            stamp = st.st_mtime

            if (stamp + diff) >= nowts:
                continue

            newpath = pathname_replace(oldpath, src, dst)
            assert oldpath != newpath

            os.makedirs(os.path.dirname(newpath), exist_ok=True)

            path_exists = os.path.exists(newpath)
            same_file = path_exists and same_content(oldpath, newpath)

            if os.path.exists(newpath) and not same_file:
                msg = ("Moving '{old}' -> '{new}'. Destination file "
                       "exists but has different content")
                raise NotImplementedError(msg)

            if not os.path.exists(newpath):
                if not dry_run:
                    shutil.move(oldpath, newpath)
                ret.append((Operations.MOVE, oldpath, newpath))

            else:
                if not dry_run:
                    print("rm '{}'".format(oldpath))
                ret.append((Operations.UNLINK, oldpath))

    return ret


def pathname_replace(pathname, fragment, replacement):
    fragment = pathname_split(fragment)
    replacement = pathname_split(replacement)
    pathname = pathname_split(pathname)

    idx = hkdatatools.list_in_list(fragment, pathname)
    if idx == -1:
        return '/'.join(pathname)

    pre, post = pathname[0:idx], pathname[idx+len(fragment):]
    return '/'.join(pre + replacement + post)


def pathname_normalize(p):
    return humanfriendly.parse_path(p)


def pathname_split(p):
    is_absolute = p[0] == '/'
    parts = p.split('/')
    parts = [x for x in parts if x]

    if is_absolute:
        parts = [''] + parts

    return parts


def pathname_for_uri(uri):
    parsed = parse.urlparse(uri)
    if parsed.scheme != 'file':
        raise ValueError(uri)

    return parse.unquote(parsed.path)


def same_content(file_a, file_b):
    with open(file_a, 'rb') as fh:
        a = hkdigest.digest(fh)

    with open(file_b, 'rb') as fh:
        b = hkdigest.digest(fh)

    return a == b
