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
import tempfile
import subprocess


def is_archivable(filename, now_timestamp, delta):
    st = os.stat(filename)
    stamp = st.st_mtime

    return (stamp + delta) < now_timestamp


def transfer(src, dst, filenames, move=False, dry_run=True):
    
    # For a detailed explanation of rsync itemized changes output see:
    # http://stackoverflow.com/a/36851784

    src = hktools.pathname_ensure_slash(src)
    dst = hktools.pathname_ensure_slash(dst)

    rsync_cmdl = [
        '/usr/bin/rsync',
        '--delete',
        '--delete-after',
        '--itemize-changes',
        '--recursive',
        '--times',
        # '--verbose',
    ]

    if move:
        rsync_cmdl.append('--remove-source-files')

    if True or dry_run:
        rsync_cmdl.append('--dry-run')

    src_len = len(src)
    assert all([filename.startswith(src) for filename in filenames])
    filenames = [filename[src_len:] for filename in filenames]

    # Write files from
    fd, filesfrom_filename = tempfile.mkstemp()
    with os.fdopen(fd, mode='w') as fh:
        fh.write("\n".join(filenames) + "\n")
    rsync_cmdl.extend(['--files-from', filesfrom_filename])

    rsync_cmdl.extend([src, dst])

    print(rsync_cmdl)
    try:
        output = subprocess.check_output(rsync_cmdl).decode('utf-8')
    except subprocess.CalledProcessError as e:
        pass

    os.unlink(filesfrom_filename)
    print(output)


def main(source, destination, delta=4*7*24*60*60, now=None):
    if now is None:
        now = hktools.now()

    filelist = hktools.filelist_for_pathname(src)
    archivables = list(filter(
        lambda x: is_archivable(x, now_timestamp=now, delta=delta),
        filelist
    ))

    transfer(src, dst, archivables)

    print('{} items'.format(len(archivables)))


if __name__ == '__main__':
    src = path.expanduser('~/Sync/WhatsApp Media')
    dst = path.expanduser('~/Sync/WhatsApp Media (Archive)')

    main(src, dst)
