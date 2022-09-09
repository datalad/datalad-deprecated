#!/usr/bin/env python

import sys
from setuptools import setup
import versioneer

from _datalad_buildsupport.setup import (
    BuildManPage,
)

cmdclass = versioneer.get_cmdclass()
cmdclass.update(build_manpage=BuildManPage)

# Give setuptools a hint to complain if it's too old a version
# 43.0.0 allows us to put most metadata in setup.cfg and causes pyproject.toml
# to be automatically included in sdists
# Should match pyproject.toml
SETUP_REQUIRES = ['setuptools >= 43.0.0']
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ['wheel'] if 'bdist_wheel' in sys.argv else []

if __name__ == '__main__':
    setup(name='datalad_deprecated',
          version=versioneer.get_version(),
          cmdclass=cmdclass,
          setup_requires=SETUP_REQUIRES,
          entry_points={
              'datalad.extensions': [
                  'deprecated=datalad_deprecated:command_suite',
              ],
              'datalad.metadata.extractors': [
                  'annex=datalad_deprecated.metadata.extractors.annex:MetadataExtractor',
                  'audio=datalad_deprecated.metadata.extractors.audio:MetadataExtractor',
                  'datacite=datalad_deprecated.metadata.extractors.datacite:MetadataExtractor',
                  'datalad_core=datalad_deprecated.metadata.extractors.datalad_core:MetadataExtractor',
                  'datalad_rfc822=datalad_deprecated.metadata.extractors.datalad_rfc822:MetadataExtractor',
                  'exif=datalad_deprecated.metadata.extractors.exif:MetadataExtractor',
                  'frictionless_datapackage=datalad_deprecated.metadata.extractors.frictionless_datapackage:MetadataExtractor',
                  'image=datalad_deprecated.metadata.extractors.image:MetadataExtractor',
                  'xmp=datalad_deprecated.metadata.extractors.xmp:MetadataExtractor',
              ]
          },
    )

