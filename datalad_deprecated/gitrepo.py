# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Internal low-level interface to Git repositories

"""

import os.path as op

import logging
from os.path import (
    join as opj,
    exists,
    isabs,
    curdir,
)

import posixpath
import warnings

from datalad.utils import (
    Path,
    posix_relpath,
)

from datalad.support.gitrepo import (
    GitRepo,
)
from datalad.support.exceptions import (
    InvalidGitRepositoryError,
)
from datalad.core.local.repo import repo_from_path

lgr = logging.getLogger('datalad.gitrepo')


class DeprecatedGitRepoMethods(object):
    """This class is just a container for GitRepo methods that have been deprecated
    in -core. The can be moved here to rot in peace.
    """

    def add_submodule(self, path, name=None, url=None, branch=None):
        """Add a new submodule to the repository.

        This will alter the index as well as the .gitmodules file, but will not
        create a new commit.  If the submodule already exists, no matter if the
        configuration differs from the one provided, the existing submodule
        is considered as already added and no further action is performed.

        NOTE: This method does not work with submodules that use git-annex adjusted
              branches. Use Repo.save() instead.

        Parameters
        ----------
        path : str
          repository-relative path at which the submodule should be located, and
          which will be created as required during the repository initialization.
        name : str or None
          name/identifier for the submodule. If `None`, the `path` will be used
          as name.
        url : str or None
          git-clone compatible URL. If `None`, the repository is assumed to
          exist, and the url of the first remote is taken instead. This is
          useful if you want to make an existing repository a submodule of
          another one.
        branch : str or None
          name of branch to be checked out in the submodule. The given branch
          must exist in the remote repository, and will be checked out locally
          as a tracking branch. If `None`, remote HEAD will be checked out.
        """
        warnings.warn(
            'GitRepo.add_submodule() is deprecated and will be removed in '
            'a future release. Use the Dataset method save() instead.',
            DeprecationWarning
        )

        if name is None:
            name = Path(path).as_posix()
        cmd = ['submodule', 'add', '--name', name]
        if branch is not None:
            cmd += ['-b', branch]
        if url is None:
            # repo must already exist locally
            subm = repo_from_path(op.join(self.path, path))
            # check that it has a commit, and refuse
            # to operate on it otherwise, or we would get a bastard
            # submodule that cripples git operations
            if not subm.get_hexsha():
                raise InvalidGitRepositoryError(
                    'cannot add subdataset {} with no commits'.format(subm))
            # make an attempt to configure a submodule source URL based on the
            # discovered remote configuration
            remote, branch = subm.get_tracking_branch()
            url = subm.get_remote_url(remote) if remote else None

        if url is None:
            # had no luck with a remote URL
            if not isabs(path):
                # need to recode into a relative path "URL" in POSIX
                # style, even on windows
                url = posixpath.join(curdir, posix_relpath(path))
            else:
                url = path
        cmd += [url, Path(path).as_posix()]
        self.call_git(cmd)
        # record dataset ID if possible for comprehesive metadata on
        # dataset components within the dataset itself
        subm_id = GitRepo(op.join(self.path, path)).config.get(
            'datalad.dataset.id', None)
        if subm_id:
            self.call_git(
                ['config', '--file', '.gitmodules', '--replace-all',
                 'submodule.{}.datalad-id'.format(name), subm_id])
        # ensure supported setup
        from datalad.support.gitrepo import _fixup_submodule_dotgit_setup
        _fixup_submodule_dotgit_setup(self, path)
        # TODO: return value

    def deinit_submodule(self, path, **kwargs):
        """Deinit a submodule

        Parameters
        ----------
        path: str
            path to the submodule; relative to `self.path`
        kwargs:
            see `__init__`
        """
        warnings.warn(
            'GitRepo.deinit_submodule() is deprecated and will be removed in '
            'a future release. Use call_git() instead.',
            DeprecationWarning
        )
        from datalad.support.gitrepo import to_options
        self.call_git(['submodule', 'deinit'] + to_options(**kwargs),
                      files=[path])
        # TODO: return value

    def update_submodule(self, path, mode='checkout', init=False):
        """Update a registered submodule.

        This will make the submodule match what the superproject expects by
        cloning missing submodules and updating the working tree of the
        submodules. The "updating" can be done in several ways depending
        on the value of submodule.<name>.update configuration variable, or
        the `mode` argument.

        Parameters
        ----------
        path : str
          Identifies which submodule to operate on by it's repository-relative
          path.
        mode : {checkout, rebase, merge}
          Update procedure to perform. 'checkout': the commit recorded in the
          superproject will be checked out in the submodule on a detached HEAD;
          'rebase': the current branch of the submodule will be rebased onto
          the commit recorded in the superproject; 'merge': the commit recorded
          in the superproject will be merged into the current branch in the
          submodule.
        init : bool
          If True, initialize all submodules for which "git submodule init" has
          not been called so far before updating.
          Primarily provided for internal purposes and should not be used directly
          since would result in not so annex-friendly .git symlinks/references
          instead of full featured .git/ directories in the submodules
        """
        warnings.warn(
            'GitRepo.update_submodule() is deprecated and will be removed in '
            'a future release. Use the dataset method update() instead.',
            DeprecationWarning
        )
        if GitRepo.is_valid_repo(self.pathobj / path):
            subrepo = GitRepo(self.pathobj / path, create=False)
            subbranch = subrepo.get_active_branch() if subrepo else None
            try:
                subbranch_hexsha = subrepo.get_hexsha(subbranch) if subrepo else None
            except ValueError:
                if subrepo.commit_exists("HEAD"):
                    # Not what we thought it was. Reraise.
                    raise
                else:
                    raise ValueError(
                        "Cannot add submodule that has an unborn branch "
                        "checked out: {}"
                        .format(subrepo.path))

        else:
            subrepo = None
            subbranch = None
            subbranch_hexsha = None

        cmd = ['submodule', 'update', '--%s' % mode]
        if init:
            cmd.append('--init')
            subgitpath = opj(self.path, path, '.git')
            if not exists(subgitpath):
                # TODO:  wouldn't with --init we get all those symlink'ed .git/?
                # At least let's warn
                lgr.warning(
                    "Do not use update_submodule with init=True to avoid git creating "
                    "symlinked .git/ directories in submodules"
                )
            #  yoh: I thought I saw one recently but thought it was some kind of
            #  an artifact from running submodule update --init manually at
            #  some point, but looking at this code now I worry that it was not
        self.call_git(cmd, files=[path])

        if not init:
            return

        # track branch originally cloned, only if we had a valid repo at the start
        updated_subbranch = subrepo.get_active_branch() if subrepo else None
        if subbranch and not updated_subbranch:
            # got into 'detached' mode
            # trace if current state is a predecessor of the branch_hexsha
            lgr.debug(
                "Detected detached HEAD after updating submodule %s which was "
                "in %s branch before", self.path, subbranch)
            detached_hexsha = subrepo.get_hexsha()
            if subrepo.get_merge_base(
                    [subbranch_hexsha, detached_hexsha]) == detached_hexsha:
                # TODO: config option?
                # in all likely event it is of the same branch since
                # it is an ancestor -- so we could update that original branch
                # to point to the state desired by the submodule, and update
                # HEAD to point to that location
                lgr.info(
                    "Submodule HEAD got detached. Resetting branch %s to point "
                    "to %s. Original location was %s",
                    subbranch, detached_hexsha[:8], subbranch_hexsha[:8]
                )
                branch_ref = 'refs/heads/%s' % subbranch
                subrepo.update_ref(branch_ref, detached_hexsha)
                assert(subrepo.get_hexsha(subbranch) == detached_hexsha)
                subrepo.update_ref('HEAD', branch_ref, symbolic=True)
                assert(subrepo.get_active_branch() == subbranch)
            else:
                lgr.warning(
                    "%s has a detached HEAD since cloned branch %s has another common ancestor with %s",
                    subrepo.path, subbranch, detached_hexsha[:8]
                )
        # TODO: return value
