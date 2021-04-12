# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""" Utilities """

import builtins
import sys


def safe_print(s):
    """Print with protection against UTF-8 encoding errors"""
    # A little bit of dance to be able to test this code
    print_f = getattr(builtins, "print")
    try:
        print_f(s)
    except UnicodeEncodeError:
        # failed to encode so let's do encoding while ignoring errors
        # to print at least something
        # explicit `or ascii` since somehow on buildbot it seemed to
        # return None
        s = s.encode(
            getattr(sys.stdout, 'encoding', 'ascii') \
            or 'ascii', errors='ignore') \
            if hasattr(s, 'encode') else s
        print_f(s.decode())
