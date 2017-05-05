def _isbuiltintype(x, typ):
    if isinstance(x, typ):
        return x

    raise TypeError(x)


def isint(x):
    return _isbuiltintype(x, int)


def isstr(x):
    return _isbuiltintype(x, str)


def isnonemptystr(x):
    if isstr(x) and x:
        return x

    raise TypeError(x)


def isfloat(x):
    return _isbuiltintype(x, float)


def isbool(x):
    return _isbuiltintype(x, bool)


def isobject(x):
    return _isbuiltintype(x, object)

def str_or_str_to_fundamentals_map(x):
    return str or \
        {str: (bool(x) or int(x) or float(x) or str(x))}
