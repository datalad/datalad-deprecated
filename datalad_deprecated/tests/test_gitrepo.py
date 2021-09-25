# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test implementation of class GitRepo

"""

import logging

import os.path as op

from datalad.tests.utils import (
    assert_false,
    assert_in,
    assert_raises,
    assert_repo_status,
    DEFAULT_BRANCH,
    eq_,
    ok_,
    SkipTest,
    swallow_logs,
    with_tempfile,
)

# we nevertheless import from -core
# which must provide all deprecated methods whenever
# this package is installed too
from datalad.support.gitrepo import GitRepo
from datalad.support.exceptions import (
    CommandError,
)


@with_tempfile
@with_tempfile
@with_tempfile
def test_submodule_deinit(src, subsrc, path):
    src = GitRepo(src)
    subsrc = GitRepo(subsrc)
    for repo in (src, subsrc):
        for filename in ('some1.txt', 'some2.dat'):
            with open(op.join(repo.path, filename), 'w') as f:
                f.write(filename)
            repo.add(filename)
        repo.commit('Some files')
    src.add_submodule('subm 1', name='subm 1', url=subsrc.path)
    src.add_submodule('2', name='2', url=subsrc.path)
    src.commit('submodule added')

    top_repo = GitRepo.clone(src.path, path)
    eq_({'subm 1', '2'},
        {s["gitmodule_name"] for s in top_repo.get_submodules_()})
    # note: here init=True is ok, since we are using it just for testing
    with swallow_logs(new_level=logging.WARN) as cml:
        top_repo.update_submodule('subm 1', init=True)
        assert_in('Do not use update_submodule with init=True', cml.out)
    top_repo.update_submodule('2', init=True)

    # ok_(all([s.module_exists() for s in top_repo.get_submodules()]))
    # TODO: old assertion above if non-bare? (can't use "direct mode" in test_gitrepo)
    # Alternatively: New testrepo (plain git submodules) and have a dedicated
    # test for annexes in addition
    ok_(all(GitRepo.is_valid_repo(s["path"])
            for s in top_repo.get_submodules_()))

    # modify submodule:
    with open(op.join(top_repo.path, 'subm 1', 'file_ut.dat'), "w") as f:
        f.write("some content")

    assert_raises(CommandError, top_repo.deinit_submodule, 'sub1')

    # using force should work:
    top_repo.deinit_submodule('subm 1', force=True)

    ok_(not GitRepo.is_valid_repo(str(top_repo.pathobj / 'subm 1')))


@with_tempfile(mkdir=True)
@with_tempfile(mkdir=True)
def test_GitRepo_add_submodule(source_path, path):
    source = GitRepo(source_path, create=True)
    with open(op.join(source_path, 'some.txt'), 'w') as f:
        f.write("New text file.")
    source.add('some.txt')
    source.commit('somefile')

    top_repo = GitRepo(path, create=True)

    top_repo.add_submodule('sub', name='sub', url=source_path)
    top_repo.commit('submodule added')
    eq_([s["gitmodule_name"] for s in top_repo.get_submodules_()],
        ['sub'])
    assert_repo_status(path)
    assert_repo_status(op.join(path, 'sub'))


def test_GitRepo_update_submodule():
    raise SkipTest("TODO")


@with_tempfile(mkdir=True)
def check_update_submodule_init_adjust_branch(is_ancestor, path):
    src = GitRepo(op.join(path, "src"), create=True)
    src_sub = GitRepo(op.join(src.path, "sub"), create=True)
    src_sub.commit(msg="c0", options=["--allow-empty"])
    src_sub.commit(msg="c1", options=["--allow-empty"])
    src.add_submodule('sub', name='sub')
    src.commit(msg="Add submodule")

    # Move subdataset past the registered commit...
    hexsha_registered = src_sub.get_hexsha()
    if is_ancestor:
        # ... where the registered commit is an ancestor of the new one.
        src_sub.commit(msg="c2", options=["--allow-empty"])
    else:
        # ... where the registered commit is NOT an ancestor of the new one.
        src_sub.call_git(["reset", "--hard", DEFAULT_BRANCH + "~1"])  # c0
    hexsha_sub = src_sub.get_hexsha()

    clone = GitRepo.clone(url=src.path,
                          path=op.join(path, "clone"),
                          create=True)
    clone_sub = GitRepo.clone(url=src_sub.path,
                              path=op.join(clone.path, "sub"),
                              create=True)
    ok_(clone.dirty)
    eq_(clone_sub.get_active_branch(), DEFAULT_BRANCH)
    eq_(hexsha_sub, clone_sub.get_hexsha())

    clone.update_submodule("sub", init=True)

    assert_false(clone.dirty)
    eq_(hexsha_registered, clone_sub.get_hexsha())
    if is_ancestor:
        eq_(clone_sub.get_active_branch(), DEFAULT_BRANCH)
    else:
        assert_false(clone_sub.get_active_branch())


def test_GitRepo_update_submodule_init_adjust_branch():
    yield check_update_submodule_init_adjust_branch, True
    yield check_update_submodule_init_adjust_branch, False


@with_tempfile
def test_update_submodules_sub_on_unborn_branch(path):
    repo = GitRepo(path, create=True)
    repo.commit(msg="c0", options=["--allow-empty"])
    subrepo = GitRepo(op.join(path, "sub"), create=True)
    subrepo.commit(msg="s c0", options=["--allow-empty"])
    repo.add_submodule(path="sub")
    subrepo.checkout("other", options=["--orphan"])
    with assert_raises(ValueError) as cme:
        repo.update_submodule(path="sub")
    assert_in("unborn branch", str(cme.exception))


@with_tempfile
def test_GitRepo_get_submodules(path):
    repo = GitRepo(path, create=True)

    s_abc = GitRepo(op.join(path, "s_abc"), create=True)
    s_abc.commit(msg="c s_abc", options=["--allow-empty"])
    repo.add_submodule(path="s_abc")

    s_xyz = GitRepo(op.join(path, "s_xyz"), create=True)
    s_xyz.commit(msg="c s_xyz", options=["--allow-empty"])
    repo.add_submodule(path="s_xyz")

    eq_([s["gitmodule_name"]
         for s in repo.get_submodules(sorted_=True)],
        ["s_abc", "s_xyz"])


@with_tempfile
def test_get_submodules_parent_on_unborn_branch(path):
    repo = GitRepo(path, create=True)
    subrepo = GitRepo(op.join(path, "sub"), create=True)
    subrepo.commit(msg="s", options=["--allow-empty"])
    repo.add_submodule(path="sub")
    eq_([s["gitmodule_name"] for s in repo.get_submodules_()],
        ["sub"])
