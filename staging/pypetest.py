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


import asyncio
import os


class _Packet:
    def __init__(self, data):
        self.data = data


class DataPacket(_Packet):
    pass


class EOFPacket(_Packet):
    def __init__(self):
        super().__init__(None)


class Source:
    def __init__(self):
        self.sinks = {}

    def set_sink(self, name, queue):
        self.sinks[name] = queue

    @asyncio.coroutine
    def push(self, data, name='default'):
        yield from self.sinks[name].put(DataPacket(data))

    @asyncio.coroutine
    def close(self, name='default'):
        yield from self.sinks[name].put(EOFPacket())

class Sink:
    def __init__(self):
        self.sources = {}

    def set_source(self, name, queue):
        self.sources[name] = queue

    @asyncio.coroutine
    def pull(self, name='default'):
        pkt = yield from self.sources[name].get()
        if isinstance(pkt, EOFPacket):
            raise EOFError

        return pkt.data


class Pipeline:
    def __init__(self):
        self.elements = set()

    def connect(self, src, sink):
        q = asyncio.Queue()
        src.set_sink('default', q)
        sink.set_source('default', q)
        self.elements.add(src)
        self.elements.add(sink)

    def start(self):
        fut = asyncio.gather(*[x.process() for x in self.elements])
        asyncio.get_event_loop().run_until_complete(fut)

class FileFinderSource(Source):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def process(self):
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for filename in filenames:
                filepath = dirpath + '/' + filename
                yield from self.push(filepath)

        yield from self.close()


class Printer(Sink):
    def __init__(self):
        super().__init__()

    def process(self):
        while True:
            try:
                x = (yield from self.pull())
            except EOFError:
                break

            print('==>', x)

        print ('got eof')

pl = Pipeline()
pl.connect(FileFinderSource('/tmp'), Printer())
pl.start()

# nowts = hktools.now()


# # ==================================
# import functools

# def generator_unroll(fn):
#     @functools.wraps(fn)
#     def wrapper(*args, **kwargs):
#         return [x for x in fn(*args, **kwargs)]

#     return wrapper

# @generator_unroll
# def get_file_list(path):
#     for (dirpath, dirnames, filenames) in os.walk(path):
#         for filename in filenames:
#             yield dirpath + '/' + filename


# def filter_older_than(delta)

# # ==================================


# def archive(src, dst, diff, filter_func=None):
#     for (dirpath, dirnames, filenames) in os.walk(src):
#         if filter_func:
#             filter_func(dirpath, dirnames, filenames)

#         for filename in filenames:
#             oldpath = dirpath + '/' + filename
#             st = os.stat(oldpath)
#             stamp = st.st_mtime

#             if (stamp + diff) >= nowts:
#                 continue

#             newpath = hktools.pathname_replace(oldpath, src, dst)
#             assert oldpath != newpath

#             try:
#                 os.makedirs(path.dirname(newpath))
#             except OSError:
#                 pass

#             if not path.exists(newpath):
#                 print('mv "{}" "{}"'.format(oldpath, newpath))
#             else:
#                 if hktools.same_content(oldpath, newpath):
#                     print("rm '{}'".format(oldpath))
#                 else:
#                     print("# unhandled case for '{}' '{}'".format(oldpath, newpath))


# def btsyncdir_filter(dirpath, dirnames, filenames):
#     try:
#         dirnames.remove('.sync')
#     except ValueError:
#         pass

#     hidden = [x for x in filenames if x[0] == '.']
#     for x in hidden:
#         filenames.remove(x)

# if __name__ == '__main__':
#     archive(
#         path.expanduser('~/Sync/WhatsApp Media'),
#         path.expanduser('~/Sync/WhatsApp Media (Archive)'),
#         diff=28*24*60*60,
#         filter_func=btsyncdir_filter)
