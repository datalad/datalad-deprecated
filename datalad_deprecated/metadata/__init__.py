# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Metadata handling (parsing, storing, querying)"""

import datalad.interface.common_cfg as config_module
from datalad.support.constraints import (
    EnsureBool,
    EnsureChoice,
    EnsureInt,
)


# We have to add the metadata specific default
# to the general config definitions to support
# metadata commands that ask for this config.

config_module.definitions['datalad.search.default-mode'] = {
    'ui': (
        'question', {
            'title': 'Default search mode',
            'text': 'Label of the mode to be used by default'
        }
    ),
    'type': EnsureChoice('egrep', 'textblob', 'autofield'),
    'default': 'egrep',
}

config_module.definitions['datalad.search.index-default-documenttype'] = {
    'ui': (
        'question', {
            'title': 'Type of search index documents',
            'text': 'Labels of document types to include in a default search index'
        }
    ),
    'type': EnsureChoice('all', 'datasets', 'files'),
    'default': 'datasets',
}

config_module.definitions['datalad.search.indexercachesize'] = {
    'ui': (
        'question', {
            'title': 'Maximum cache size for search index (per process)',
            'text': 'Actual memory consumption can be twice as high as this value in MB (one process per CPU is used)'
        }
    ),
    'default': 256,
    'type': EnsureInt(),
}

config_module.definitions['datalad.metadata.maxfieldsize'] = {
    'ui': (
        'question', {
            'title': 'Maximum metadata field size',
            'text': 'Metadata fields exceeding this size (in bytes/chars) are excluded from metadata extractio'
        }
    ),
    'default': 100000,
    'type': EnsureInt(),
}

config_module.definitions['datalad.metadata.nativetype'] = {
    'ui': (
        'question', {
            'title': 'Native dataset metadata scheme',
            'text': 'Set this label to engage a particular metadata extraction parser'
        }
    ),
}

config_module.definitions['datalad.metadata.store-aggregate-content'] = {
    'ui': (
        'question', {
            'title': 'Aggregated content metadata storage',
            'text': 'If this flag is enabled, content metadata is aggregated into superdataset to allow for discovery of individual files. If disable unique content metadata values are still aggregated to enable dataset discovery'
        }
    ),
    'type': EnsureBool(),
    'default': True,
}

config_module.definitions['datalad.metadata.create-aggregate-annex-limit'] = {
    'ui': (
        'question', {
            'title': 'Limit configuration annexing aggregated metadata in new dataset',
            'text': 'Git-annex large files expression (see https://git-annex.branchable.com/tips/largefiles; given expression will be wrapped in parentheses)'
        }
    ),
    'default': 'anything',
}
