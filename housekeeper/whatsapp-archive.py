#!/usr/bin/env python3

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
