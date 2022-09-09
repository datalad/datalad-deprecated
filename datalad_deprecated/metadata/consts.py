from os.path import join

from datalad.consts import DATALAD_DOTDIR


# Make use of those in datalad.metadata
OLDMETADATA_DIR = join(DATALAD_DOTDIR, 'meta')
OLDMETADATA_FILENAME = 'meta.json'

METADATA_DIR = join(DATALAD_DOTDIR, 'metadata')
DATASET_METADATA_FILE = join(METADATA_DIR, 'dataset.json')

SEARCH_INDEX_DOTGITDIR = join('datalad', 'search_index')
