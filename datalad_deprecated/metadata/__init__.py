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
    EnsureChoice,
    EnsureInt,
)


# We have to add the metadata specific default
# to the general config definitions to support
# metadata commands that ask for this config.
config_module.definitions['datalad.search.default-mode'] = {
    'ui': ('question', {
        'title': 'Default search mode',
        'text': 'Label of the mode to be used by default'}),
    'type': EnsureChoice('egrep', 'textblob', 'autofield'),
    'default': 'egrep',
}

config_module.definitions['datalad.metadata.maxfieldsize'] = {
    'ui': ('question', {
        'title': 'Maximum metadata field size',
        'text': 'Metadata fields exceeding this size (in bytes/chars) are excluded from metadata extractio'}),
    'default': 100000,
    'type': EnsureInt(),
}

config_module.definitions['datalad.metadata.nativetype'] = {
    'ui': ('question', {
        'title': 'Native dataset metadata scheme',
        'text': 'Set this label to engage a particular metadata extraction parser'}),
}
