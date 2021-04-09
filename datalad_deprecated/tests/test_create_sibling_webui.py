# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test create publication target ssh web server action

"""

import os
import re

from os.path import (
    join as opj,
    exists,
)
from datalad.distribution.dataset import Dataset
from datalad.api import (
    create_sibling,
    install,
    publish,
)
from datalad.support.gitrepo import GitRepo
from datalad.tests.utils import (
    assert_false,
    assert_no_errors_logged,
    assert_not_in,
    ok_exists,
    ok_file_has_content,
    skip_if_on_windows,
    skip_ssh,
    slow,
    with_tempfile,
    with_testrepos,
)
from datalad.utils import (
    _path_,
    chpwd,
)
from datalad.distribution.tests.test_create_sibling \
    import assert_postupdate_hooks

import logging
lgr = logging.getLogger('datalad.deprecated')


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


if lgr.getEffectiveLevel() > logging.DEBUG:
    assert_create_sshwebserver = assert_no_errors_logged(create_sibling)
else:
    assert_create_sshwebserver = create_sibling


@slow  # 53.8496s
@with_testrepos('submodule_annex', flavors=['local'])
@with_tempfile(mkdir=True)
@with_tempfile
def check_target_ssh_recursive(use_ssh, origin, src_path, target_path):

    # prepare src
    source = install(src_path, source=origin, recursive=True)

    sub1 = Dataset(opj(src_path, "subm 1"))
    sub2 = Dataset(opj(src_path, "2"))

    for flat in False, True:
        target_path_ = target_dir_tpl = target_path + "-" + str(flat)

        if flat:
            target_dir_tpl += "/prefix%RELNAME"
            sep = '-'
        else:
            sep = os.path.sep

        if use_ssh:
            sshurl = "ssh://datalad-test" + target_path_
        else:
            sshurl = target_path_

        remote_name = 'remote-' + str(flat)
        with chpwd(source.path):
            assert_create_sshwebserver(
                name=remote_name,
                sshurl=sshurl,
                target_dir=target_dir_tpl,
                recursive=True,
                ui=True)

        # raise if git repos were not created
        for suffix in [sep + 'subm 1', sep + '2', '']:
            target_dir = opj(target_path_, 'prefix' if flat else "").rstrip(os.path.sep) + suffix
            # raise if git repos were not created
            GitRepo(target_dir, create=False)

            assert_publish_with_ui(target_dir, rootds=not suffix, flat=flat)

        for repo in [source.repo, sub1.repo, sub2.repo]:
            assert_not_in("local_target", repo.get_remotes())

        # now, push should work:
        publish(dataset=source, to=remote_name)

        # verify that we can create-sibling which was created later and possibly
        # first published in super-dataset as an empty directory
        sub3_name = 'subm 3-%s' % flat
        sub3 = source.create(sub3_name)
        # since is an empty value to force it to consider all changes since we published
        # already
        with chpwd(source.path):
            # as we discussed in gh-1495 we use the last-published state of the base
            # dataset as the indicator for modification detection with since=''
            # hence we must not publish the base dataset on its own without recursion,
            # if we want to have this mechanism do its job
            #publish(to=remote_name)  # no recursion
            assert_create_sshwebserver(
                name=remote_name,
                sshurl=sshurl,
                target_dir=target_dir_tpl,
                recursive=True,
                existing='skip',
                ui=True,
                since=''
            )
            assert_postupdate_hooks(target_path_, installed=True, flat=flat)
        # so it was created on remote correctly and wasn't just skipped
        assert(Dataset(_path_(target_path_, ('prefix-' if flat else '') + sub3_name)).is_installed())
        publish(dataset=source, to=remote_name, recursive=True, since='') # just a smoke test


@slow  # 28 + 19sec on travis
def test_target_ssh_recursive():
    skip_if_on_windows()
    yield skip_ssh(check_target_ssh_recursive), True
    yield check_target_ssh_recursive, False
