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


import hashlib
import os


def digest_for_filename(filename, digest=hashlib.sha256, block_size=8*2**20):
    m = digest()

    with open(filename, 'rb') as fh:
        while True:
            buff = fh.read(block_size)
            if not buff:
                break

            m.update(buff)

    return m.hexdigest()


def filelist_for_pathname(pathname, skip_hidden=True):
    for (dirpath, dirnames, filenames) in os.walk(pathname):
        if dirpath[0] == '.':
            continue

        hidden = (
            [(dirnames, x) for x in dirnames if x[0] == '.'] +
            [(filenames, x) for x in filenames if x[0] == '.']
        )
        for (obj, item) in hidden:
            obj.remove(item)

        for filename in filenames:
            yield dirpath + '/' + filename



def pathname_ensure_slash(pathname, start=True, end=True):
    def slash_at(x, idx):
        return x[idx] == '/'

    if start:
        pathname = pathname if slash_at(pathname, 0) else '/' + pathname

    if end:
        pathname = pathname if slash_at(pathname, -1) else pathname + '/'

    return pathname




def validate_mapping(d, required=[], optional=[], allow_other=False):
    dkeys = set(d.keys())

    missing = set()
    unknow = set()

    for x in required:
        if x not in d:
            missing.add(x)

    if not allow_other:
        unknow = dkeys - set(required) - set(optional)

    if missing or (not allow_other and unknow):
        raise MappingValidationError(list(missing), list(unknow))


class MappingValidationError(Exception):
    def __init__(self, missing, unknow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.missing = missing
        self.unknow = unknow

    def __repr__(self):
        return '<{} missing={}, unknow={}>'.format(
            self.__class__.__name__,
            repr(self.missing),
            repr(self.unknow))
