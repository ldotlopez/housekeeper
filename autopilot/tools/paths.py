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