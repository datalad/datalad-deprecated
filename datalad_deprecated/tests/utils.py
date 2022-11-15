import logging
import pytest
import re
import tempfile

from functools import wraps
from os.path import join as opj

from datalad import cfg as dl_cfg
from datalad.api import create
from datalad.cmd import (
    GitWitlessRunner,
    KillOutput,
)
from datalad.support.gitrepo import GitRepo
from datalad.support.annexrepo import AnnexRepo
from datalad.utils import (
    optional_args,
    is_explicit_path,
    get_tempfile_kwargs,
)
from datalad.tests.utils import (
    rmtemp,
)
from datalad.tests.utils_pytest import (
    assert_false,
    attr,
    _get_resolved_flavors,
    create_tree,
)

from datalad.tests import _TEMP_PATHS_GENERATED

lgr = logging.getLogger("datalad.tests.utils_pytest")
_TESTREPOS = None
local_testrepo_flavors = ['local'] # 'local-url'
_TEMP_PATHS_CLONES = set()

if dl_cfg.obtain('datalad.tests.setup.testrepos'):
    lgr.debug("Pre-populating testrepos")
    from datalad_deprecated.tests.utils import with_testrepos

    with_testrepos()(lambda repo: 1)()


@optional_args
def with_testrepos(t, regex='.*', flavors='auto', skip=False, count=None):
    """Decorator to provide a local/remote test repository

    All tests under datalad/tests/testrepos are stored in two-level hierarchy,
    where top-level name describes nature/identifier of the test repository,
    and there could be multiple instances (e.g. generated differently) of the
    same "content"

    Parameters
    ----------
    regex : string, optional
      Regex to select which test repos to use
    flavors : {'auto', 'local', 'local-url', 'clone', 'network', 'network-clone'} or list of thereof, optional
      What URIs to provide.  E.g. 'local' would just provide path to the
      repository, while 'network' would provide url of the remote location
      available on Internet containing the test repository.  'clone' would
      clone repository first to a temporary location. 'network-clone' would
      first clone from the network location. 'auto' would include the list of
      appropriate ones (e.g., no 'network*' flavors if network tests are
      "forbidden").
    count: int, optional
      If specified, only up to that number of repositories to test with

    Examples
    --------

    >>> from datalad_deprecated.tests.utils_pytest import with_testrepos
    >>> @with_testrepos('basic_annex')
    ... def test_write(repo):
    ...    assert(os.path.exists(os.path.join(repo, '.git', 'annex')))

    """
    @wraps(t)
    @attr('with_testrepos')
    def  _wrap_with_testrepos(*arg, **kw):
        # addurls with our generated file:// URLs doesn't work on appveyor
        # https://ci.appveyor.com/project/mih/datalad/builds/29841505/job/330rwn2a3cvtrakj
        #if 'APPVEYOR' in os.environ:
        #    pytest.skip("Testrepo setup is broken on AppVeyor")
        # TODO: would need to either avoid this "decorator" approach for
        # parametric tests or again aggregate failures like sweepargs does
        flavors_ = _get_resolved_flavors(flavors)

        testrepos_uris = _get_testrepos_uris(regex, flavors_)
        # we should always have at least one repo to test on, unless explicitly only
        # network was requested by we are running without networked tests
        if not (dl_cfg.get('datalad.tests.nonetwork') and flavors == ['network']):
            assert(testrepos_uris)
        else:
            if not testrepos_uris:
                pytest.skip("No non-networked repos to test on")

        fake_dates = dl_cfg.get("datalad.fake-dates")
        ntested = 0
        for uri in testrepos_uris:
            if count and ntested >= count:
                break
            ntested += 1
            if __debug__:
                lgr.debug('Running %s on %s', t.__name__, uri)
            try:
                t(*(arg + (uri,)), **kw)
            finally:
                # The is_explicit_path check is needed because it may be a URL,
                # but check_dates needs a local path or GitRepo object.
                if fake_dates and is_explicit_path(uri):
                    from datalad.support.repodates import check_dates
                    assert_false(
                        check_dates(uri, annex="tree")["objects"])
                if uri in _TEMP_PATHS_CLONES:
                    _TEMP_PATHS_CLONES.discard(uri)
                    rmtemp(uri)
                pass  # might need to provide additional handling so, handle
    return  _wrap_with_testrepos
with_testrepos.__test__ = False



def _get_testrepos_uris(regex, flavors):
    global _TESTREPOS
    # we should instantiate those whenever test repos actually asked for
    # TODO: just absorb all this lazy construction within some class
    if not _TESTREPOS:
        from datalad.tests.utils_testrepos import (
            BasicAnnexTestRepo,
            BasicGitTestRepo,
            InnerSubmodule,
            NestedDataset,
            SubmoduleDataset,
        )

        _basic_annex_test_repo = BasicAnnexTestRepo()
        _basic_git_test_repo = BasicGitTestRepo()
        _submodule_annex_test_repo = SubmoduleDataset()
        _nested_submodule_annex_test_repo = NestedDataset()
        _inner_submodule_annex_test_repo = InnerSubmodule()
        _TESTREPOS = {'basic_annex':
                        {'network': 'https://github.com/datalad/testrepo--basic--r1',
                         'local': _basic_annex_test_repo.path,
                         'local-url': _basic_annex_test_repo.url},
                      'basic_git':
                        {'local': _basic_git_test_repo.path,
                         'local-url': _basic_git_test_repo.url},
                      'submodule_annex':
                        {'local': _submodule_annex_test_repo.path,
                         'local-url': _submodule_annex_test_repo.url},
                      'nested_submodule_annex':
                        {'local': _nested_submodule_annex_test_repo.path,
                         'local-url': _nested_submodule_annex_test_repo.url},
                      # TODO: append 'annex' to the name:
                      # Currently doesn't work with some annex tests, despite
                      # working manually. So, figure out how the tests' setup
                      # messes things up with this one.
                      'inner_submodule':
                        {'local': _inner_submodule_annex_test_repo.path,
                         'local-url': _inner_submodule_annex_test_repo.url}
                      }
        # assure that now we do have those test repos created -- delayed
        # their creation until actually used
        _basic_annex_test_repo.create()
        _basic_git_test_repo.create()
        _submodule_annex_test_repo.create()
        _nested_submodule_annex_test_repo.create()
        _inner_submodule_annex_test_repo.create()
    uris = []
    for name, spec in _TESTREPOS.items():
        if not re.match(regex, name):
            continue
        uris += [spec[x] for x in set(spec.keys()).intersection(flavors)]

        # additional flavors which might have not been
        if 'clone' in flavors and 'clone' not in spec:
            uris.append(clone_url(spec['local']))

        if 'network-clone' in flavors \
                and 'network' in spec \
                and 'network-clone' not in spec:
            uris.append(clone_url(spec['network']))

    return uris


def clone_url(url):
    runner = GitWitlessRunner()
    tdir = tempfile.mkdtemp(**get_tempfile_kwargs(
        {'dir': dl_cfg.get("datalad.tests.temp.dir")}, prefix='clone_url'))
    runner.run(["git", "clone", url, tdir], protocol=KillOutput)
    if GitRepo(tdir).is_with_annex():
        AnnexRepo(tdir, init=True)
    _TEMP_PATHS_CLONES.add(tdir)
    return tdir



def make_studyforrest_mockup(path):
    """Generate a dataset structure mimicking aspects of studyforrest.org

    Under the given path there are two directories:

    public - to be published datasets
    private - never to be published datasets

    The 'public' directory itself is a superdataset, the 'private' directory
    is just a directory that contains standalone datasets in subdirectories.
    """
    public = create(opj(path, 'public'), description="umbrella dataset")
    # the following tries to capture the evolution of the project
    phase1 = public.create('phase1',
                           description='old-style, no connection to RAW')
    structural = public.create('structural', description='anatomy')
    tnt = public.create('tnt', description='image templates')
    tnt.clone(source=phase1.path, path=opj('src', 'phase1'), reckless='auto')
    tnt.clone(source=structural.path, path=opj('src', 'structural'), reckless='auto')
    aligned = public.create('aligned', description='aligned image data')
    aligned.clone(source=phase1.path, path=opj('src', 'phase1'), reckless='auto')
    aligned.clone(source=tnt.path, path=opj('src', 'tnt'), reckless='auto')
    # new acquisition
    labet = create(opj(path, 'private', 'labet'), description="raw data ET")
    phase2_dicoms = create(opj(path, 'private', 'p2dicoms'), description="raw data P2MRI")
    phase2 = public.create('phase2',
                           description='new-style, RAW connection')
    phase2.clone(source=labet.path, path=opj('src', 'labet'), reckless='auto')
    phase2.clone(source=phase2_dicoms.path, path=opj('src', 'dicoms'), reckless='auto')
    # add to derivatives
    tnt.clone(source=phase2.path, path=opj('src', 'phase2'), reckless='auto')
    aligned.clone(source=phase2.path, path=opj('src', 'phase2'), reckless='auto')
    # never to be published media files
    media = create(opj(path, 'private', 'media'), description="raw data ET")
    # assuming all annotations are in one dataset (in reality this is also
    # a superdatasets with about 10 subdatasets
    annot = public.create('annotations', description='stimulus annotation')
    annot.clone(source=media.path, path=opj('src', 'media'), reckless='auto')
    # a few typical analysis datasets
    # (just doing 3, actual status quo is just shy of 10)
    # and also the real goal -> meta analysis
    metaanalysis = public.create('metaanalysis', description="analysis of analyses")
    for i in range(1, 3):
        ana = public.create('analysis{}'.format(i),
                            description='analysis{}'.format(i))
        ana.clone(source=annot.path, path=opj('src', 'annot'), reckless='auto')
        ana.clone(source=aligned.path, path=opj('src', 'aligned'), reckless='auto')
        ana.clone(source=tnt.path, path=opj('src', 'tnt'), reckless='auto')
        # link to metaanalysis
        metaanalysis.clone(source=ana.path, path=opj('src', 'ana{}'.format(i)),
                           reckless='auto')
        # simulate change in an input (but not raw) dataset
        create_tree(
            aligned.path,
            {'modification{}.txt'.format(i): 'unique{}'.format(i)})
        aligned.save()
    # finally aggregate data
    aggregate = public.create('aggregate', description='aggregate data')
    aggregate.clone(source=aligned.path, path=opj('src', 'aligned'), reckless='auto')
    # the toplevel dataset is intentionally left dirty, to reflect the
    # most likely condition for the joint dataset to be in at any given
    # point in time
