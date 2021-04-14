# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from unittest.mock import patch
from io import StringIO
from tempfile import NamedTemporaryFile
from datalad.tests.utils import (
    assert_equal,
    skip_if_on_windows,
    SkipTest,
)

from datalad import __main__
from ..auto import AutomagicIO


# automagic IO is not supported on windows
@skip_if_on_windows
@patch.object(AutomagicIO, 'activate')
@patch('sys.stdout', new_callable=StringIO)
def test_main_run_a_script(stdout, mock_activate):
    try:
        from datalad.auto import AutomagicIO
        raise SkipTest(
            'Test not compatible with DataLad that provides AutomagicIO '
            'itself')
    except ModuleNotFoundError:
        pass
    f = NamedTemporaryFile()
    f.write('print("Running the script")\n'.encode())
    f.flush()
    __main__.main(['__main__.py', f.name])
    assert_equal(stdout.getvalue().rstrip(), "Running the script")
    # And we have "activated"
    mock_activate.assert_called_once_with()
