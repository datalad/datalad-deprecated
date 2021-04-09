# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test create publication target ssh web server action

"""

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
