"""DataLad extension for deprecated functionality"""

__docformat__ = 'restructuredtext'


# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "Deprecated functionality",
    [
        (
            'datalad_deprecated.ls',
            'Ls',
        ),
        (
            'datalad_deprecated.publish',
            'Publish',
        ),
        (
            'datalad_deprecated.annotate_paths',
            'AnnotatePaths',
        ),
        (
            'datalad_deprecated.metadata.search',
            'Search',
        ),
        (
            'datalad_deprecated.metadata.metadata',
            'Metadata',
        ),
        (
            'datalad_deprecated.metadata.extract_metadata',
            'ExtractMetadata',
            'extract-metadata',
            'extract_metadata',
        ),
        (
            'datalad_deprecated.metadata.aggregate',
            'AggregateMetaData',
            'aggregate-metadata',
            'aggregate_metadata',
        ),
    ]
)


from datalad import setup_package
from datalad import teardown_package

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
