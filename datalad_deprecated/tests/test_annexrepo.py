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

from os.path import join as opj

from datalad.support.annexrepo import AnnexRepo

from datalad.tests.utils import (
    assert_repo_status,
    eq_,
    skip_if_adjusted_branch,
    with_tempfile,
)


@skip_if_adjusted_branch
@with_tempfile
@with_tempfile
def test_AnnexRepo_add_submodule(source_path, path):
    source = AnnexRepo(source_path, create=True)
    (source.pathobj / 'test-annex.dat').write_text("content")
    source.save('some')

    top_repo = AnnexRepo(path, create=True)

    top_repo.add_submodule('sub', name='sub', url=source_path)
    top_repo.commit('submodule added')
    eq_([s["gitmodule_name"] for s in top_repo.get_submodules_()],
        ['sub'])

    assert_repo_status(top_repo, annex=True)
    assert_repo_status(opj(path, 'sub'), annex=False)
