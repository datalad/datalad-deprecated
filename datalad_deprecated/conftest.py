try:
    from datalad.conftest import setup_package
except ImportError:
    # Doesn't quite work for deprecated because of
    # - assert_raises  .exception -> .value
    # - use some of the tests from datalad core as is:
    #  datalad_deprecated/tests/test_create_sibling_webui.py:from datalad.distribution.tests.test_create_sibling import
    #  datalad_deprecated/tests/test_publish.py:from datalad.distribution.tests.test_create_sibling import
    # but kept here as an example of how it could potentially be done
    raise

    # assume old datalad without pytest support introduced in
    # https://github.com/datalad/datalad/pull/6273
    import pytest
    from datalad import setup_package as _setup_package
    from datalad import teardown_package as _teardown_package


    @pytest.fixture(autouse=True, scope="session")
    def setup_package():
        _setup_package()
        yield
        _teardown_package()
