# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test create publication target ssh web server action

"""

import re
from os.path import (
    exists,
    join as opj,
)
from datalad.utils import (
    _path_,
)
from datalad.tests.utils import (
    assert_false,
    assert_not_in,
    ok_exists,
    ok_file_has_content,
)


def assert_publish_with_ui(target_path, rootds=False, flat=True):
    paths = [_path_(".git/hooks/post-update")]     # hooks enabled in all datasets
    not_paths = []  # _path_(".git/datalad/metadata")]  # metadata only on publish
                    # ATM we run post-update hook also upon create since it might
                    # be a reconfiguration (TODO: I guess could be conditioned)

    # web-interface html pushed to dataset root
    web_paths = ['index.html', _path_(".git/datalad/web")]
    if rootds:
        paths += web_paths
    # and not to subdatasets
    elif not flat:
        not_paths += web_paths

    for path in paths:
        ok_exists(opj(target_path, path))

    for path in not_paths:
        assert_false(exists(opj(target_path, path)))

    hook_path = _path_(target_path, '.git/hooks/post-update')
    # No longer the case -- we are no longer using absolute path in the
    # script
    # ok_file_has_content(hook_path,
    #                     '.*\ndsdir="%s"\n.*' % target_path,
    #                     re_=True,
    #                     flags=re.DOTALL)
    # No absolute path (so dataset could be moved) in the hook
    with open(hook_path) as f:
        assert_not_in(target_path, f.read())
    # correct ls_json command in hook content (path wrapped in "quotes)
    ok_file_has_content(hook_path,
                        '.*datalad ls -a --json file \..*',
                        re_=True,
                        flags=re.DOTALL)


# we are simply running the tests from -core, which will behave differently
# when they find this extension to be installed. We are likely running to
# many tests for the webui scope, but that functionality is not cleanly
# separated in the tests -- but run too many than too few.
from datalad.distribution.tests.test_create_sibling import (
    test_invalid_call,
    test_target_ssh_simple,
    test_target_ssh_recursive,
    test_target_ssh_since,
    test_failon_no_permissions,
    test_replace_and_relative_sshpath,
    test_target_ssh_inherit,
    test_check_exists_interactive,
    test_local_relpath,
    test_local_path_target_dir,
    test_non_master_branch,
    test_preserve_attrs,
)
