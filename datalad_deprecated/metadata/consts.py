from os.path import join

from datalad.consts import (
    DATALAD_DOTDIR,
    DATALAD_GIT_DIR,
)


# Make use of those in datalad.metadata
OLDMETADATA_DIR = join(DATALAD_DOTDIR, 'meta')
OLDMETADATA_FILENAME = 'meta.json'

METADATA_DIR = join(DATALAD_DOTDIR, 'metadata')
WEB_META_DIR = join(DATALAD_GIT_DIR, 'metadata')

DATASET_METADATA_FILE = join(METADATA_DIR, 'dataset.json')
