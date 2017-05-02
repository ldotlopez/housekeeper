import collections
import hashlib
import os
import time
from datetime import datetime
from urllib import parse


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


def list_in_list(needle, stack):
    if needle == stack:
        return 0

    if not needle:
        return 0

    if not stack:
        return -1

    if len(needle) > len(stack):
        return -1

    needle_len = len(needle)
    for stack_idx in range(0, len(stack) - needle_len + 1):
        if stack[stack_idx:stack_idx+needle_len] == needle:
            return stack_idx

    return -1


def now():
    dt = datetime.now()
    return int(time.mktime(dt.timetuple()))


def pathname_ensure_slash(pathname, start=True, end=True):
    def slash_at(x, idx):
        return x[idx] == '/'

    if start:
        pathname = pathname if slash_at(pathname, 0) else '/' + pathname

    if end:
        pathname = pathname if slash_at(pathname, -1) else pathname + '/'

    return pathname


def pathname_for_uri(uri):
    parsed = parse.urlparse(uri)
    if parsed.scheme != 'file':
        raise ValueError(uri)

    return parse.unquote(parsed.path)


def pathname_replace(pathname, fragment, replacement):
    fragment = pathname_split(fragment)
    replacement = pathname_split(replacement)
    pathname = pathname_split(pathname)

    idx = list_in_list(fragment, pathname)
    if idx == -1:
        return '/'.join(pathname)

    pre, post = pathname[0:idx], pathname[idx+len(fragment):]
    return '/'.join(pre + replacement + post)


def pathname_split(p):
    is_absolute = p[0] == '/'
    parts = p.split('/')
    parts = [x for x in parts if x]

    if is_absolute:
        parts = [''] + parts

    return parts


def same_content(file_a, file_b):
    return digest_for_filename(file_a) == digest_for_filename(file_b)


def walk_collection(collection):
    if isinstance(collection, collections.Mapping):
        yield from ((k, v) for (k, v) in collection.items())
    else:
        yield from enumerate(collection)


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
