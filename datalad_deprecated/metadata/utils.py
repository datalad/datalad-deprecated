from datalad.support.json_py import load_stream
from datalad.utils import ensure_unicode


unicode_srctypes = str, bytes


def all_same(items):
    """Quick check if all items are the same.

    Identical to a check like len(set(items)) == 1 but
    should be more efficient while working on generators, since would
    return False as soon as any difference detected thus possibly avoiding
    unnecessary evaluations
    """
    first = True
    first_item = None
    for item in items:
        if first:
            first = False
            first_item = item
        else:
            if item != first_item:
                return False
    # So we return False if was empty
    return not first


def as_unicode(val, cast_types=object):
    """Given an arbitrary value, would try to obtain unicode value of it

    For unicode it would return original value, for python2 str or python3
    bytes it would use ensure_unicode, for None - an empty (unicode) string,
    and for any other type (see `cast_types`) - would apply the unicode
    constructor.  If value is not an instance of `cast_types`, TypeError
    is thrown

    Parameters
    ----------
    cast_types: type
      Which types to cast to unicode by providing to constructor
    """
    if val is None:
        return u''
    elif isinstance(val, str):
        return val
    elif isinstance(val, unicode_srctypes):
        return ensure_unicode(val)
    elif isinstance(val, cast_types):
        return str(val)
    else:
        raise TypeError(
            "Value %r is not of any of known or provided %s types"
            % (val, cast_types))


def load_xzstream(fname):
    yield from load_stream(fname, compressed=True)
