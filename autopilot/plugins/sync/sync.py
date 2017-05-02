import os
import sqlite3
import tempfile
from os import path

from appkit import utils as kitutils
from autopilot import tools

_registry = {}


class SyncAPI:
    def __init__(self, exclude=[]):
        self.exclude = [os.path.expanduser(x) for x in exclude]

    def archive(self, operation):
        pass

    def sync(self, operation):
        items = operation.generator.scan()

        # Strip items not under root
        n = len(operation.source)
        items = [x[n:] for x in items
                 if x.startswith(operation.source) and x != operation.source]

        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, mode='w') as fh:
            fh.write("\n".join(items) + "\n")

        args = [
            '/usr/bin/rsync',
            '--delete',
            '--delete-after',
            '--dry-run',
            '-rtv',
        ]

        exclude = operation.exclude or self.exclude
        for x in exclude:
            args.extend(['--exclude', x])

        if operation.hardlink:
            args.extend(['--link-dest', operation.source])

        args.extend([
            '--files-from', path,
            operation.source,
            operation.destination])

        print(' '.join(map(lambda x: "'{}'".format(x), args)))
        os.unlink(path)


class SyncOperation:
    def __init__(self, source, destination, generator, hardlink=False,
                 exclude=None):
        if exclude is None:
            exclude = []

        if not source or not isinstance(source, str):
            raise ValueError('Invalid source: {}'.format(source))

        if not destination or not isinstance(destination, str):
            raise ValueError('Invalid dest: {}'.format(destination))

        if not isinstance(hardlink, bool):
            raise ValueError('Invalid hardlink: {}'.format(hardlink))

        if not isinstance(exclude, list) and \
                all([isinstance(x, str) and x for x in exclude]):
            raise ValueError('Invalid exclude: {}'.format(exclude))

        self.source = tools.pathname_ensure_slash(
            os.path.expanduser(source))
        self.destination = tools.pathname_ensure_slash(
            os.path.expanduser(destination))

        self.generator = generator
        self.hardlink = hardlink
        self.exclude = [os.path.expanduser(x) for x in exclude]


def generator_factory(name, *args, **kwargs):
    try:
        cls = _registry[name]
    except KeyError as e:
        raise TypeError() from e

    return cls(*args, **kwargs)


def filter_btsyncdir(dirpath, dirnames, filenames):
    try:
        dirnames.remove('.sync')
    except ValueError:
        pass

    hidden = [x for x in filenames if x[0] == '.']
    for x in hidden:
        filenames.remove(x)


def archive(src, dst, diff, filter_func=None):
    now = kitutils.now()

    for (dirpath, dirnames, filenames) in os.walk(src):
        if filter_func:
            filter_func(dirpath, dirnames, filenames)

        for filename in filenames:
            oldpath = dirpath + '/' + filename
            st = os.stat(oldpath)
            stamp = st.st_mtime
            if (stamp + diff) < nowts:
                newpath = replace_path(src, dst, oldpath)
                assert oldpath != newpath

                try:
                    os.makedirs(path.dirname(newpath))
                except OSError:
                    pass

                print('mv "{}" "{}"'.format(oldpath, newpath))
                    # shutil.move(oldpath, newpath)



class Filesystem:
    def __init__(self, directory):
        if not isinstance(directory, str):
            raise ValueError(directory)

        if not directory:
            raise ValueError(directory)

        self.directory = tools.pathname_ensure_slash(directory)

    def scan(self):
        for (dirpath, dirs, files) in os.walk(self.directory):
            yield from (dirpath + '/' + x for x in dirs)
            yield from (dirpath + '/' + x for x in files)

_registry['filesystem'] = Filesystem


class Banshee:
    def __init__(self, playlist=None, database=None):
        if not database:
            database = path.expanduser('~/.config/banshee-1/banshee.db')

        if not playlist or not isinstance(playlist, str):
            raise ValueError(playlist)

        if not database or not isinstance(database, str):
            raise ValueError(database)

        self.playlist = playlist
        self.database = database

    def scan(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute("select PlaylistID from CorePlaylists where Name = :name",
                    {'name': self.playlist})

        res = cur.fetchone()
        if res is None:
            msg = "Playlist {name} not found"
            msg = msg.format(name=self.playlist)
            raise ValueError(msg)

        playlist_id, = res
        cur.execute(
            "select tracks.Uri from "
            "   CoreTracks as tracks join "
            "   CorePlaylistEntries as entries "
            "       on entries.TrackID = tracks.TrackID "
            "where entries.PlaylistID=:playlist_id",
            {'playlist_id': playlist_id})

        rows = cur.fetchall()
        paths = []
        for uri, in rows:
            try:
                paths.append(tools.pathname_for_uri(uri))
            except ValueError:
                pass

        return paths

_registry['banshee'] = Banshee


class Shotwell:
    def __init__(self, tags=None, score=None, database=None):
        if not database:
            database = path.expanduser('~/.local/share/shotwell/data/photo.db')

        if tags is None and score is None:
            raise ValueError('Missing tags or score')

        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValueError(score)

        if tags:
            raise ValueError('tags not supported')

        if not database or not isinstance(database, str):
            raise ValueError(database)

        self.database = database
        self.tags = tags
        self.score = score

    def scan(self):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()

        if self.score:
            query = 'select filename from PhotoTable where rating >= :rating'
            cur.execute(query, {'rating': self.score})
        else:
            raise Exception()

        return [x[0] for x in cur.fetchall()]

_registry['shotwell'] = Shotwell
