# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# -*- coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test utilities

"""

import builtins
from unittest.mock import patch

from datalad.tests.utils import assert_equal

from datalad_deprecated.utils import safe_print


def test_safe_print():
    """Just to test that we are getting two attempts to print"""

    called = [0]

    def _print(s):
        assert_equal(s, "bua")
        called[0] += 1
        if called[0] == 1:
            raise UnicodeEncodeError('crap', u"", 0, 1, 'whatever')

    with patch.object(builtins, 'print', _print):
        safe_print("bua")
    assert_equal(called[0], 2)
