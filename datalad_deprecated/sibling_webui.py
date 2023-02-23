# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Legacy code to upload a web UI to any SSH host sibling
"""

__docformat__ = 'restructuredtext'

from glob import glob
import logging
from os.path import (
    dirname,
    join as opj,
)

from datalad.consts import DATALAD_GIT_DIR
from datalad.distribution.create_sibling import mkdir_cmd
from datalad.support.sshconnector import sh_quote
from datalad.utils import (
    make_tempfile,
)
import datalad_deprecated

lgr = logging.getLogger('datalad.deprecated.sibling_webui')


WEB_HTML_DIR = opj(DATALAD_GIT_DIR, 'web')


def upload_web_interface(path, ssh, shared, ui):
    # path to web interface resources on local
    webui_local = opj(
        dirname(datalad_deprecated.__file__), 'resources', 'website')
    # local html to dataset
    html_local = opj(webui_local, "index.html")

    # name and location of web-interface html on target
    html_targetname = {True: ui, False: "index.html"}[isinstance(ui, str)]
    html_target = opj(path, html_targetname)

    # upload ui html to target
    ssh.put(html_local, html_target)

    # upload assets to the dataset
    webresources_local = opj(webui_local, 'assets')
    webresources_remote = opj(path, WEB_HTML_DIR)
    ssh('{} {}'.format(mkdir_cmd, sh_quote(webresources_remote)))
    ssh.put(webresources_local, webresources_remote, recursive=True)

    # minimize and upload js assets
    for js_file in glob(opj(webresources_local, 'js', '*.js')):
        with open(js_file) as asset:
            try:
                from jsmin import jsmin
                # jsmin = lambda x: x   # no minimization
                minified = jsmin(asset.read())                      # minify asset
            except ImportError:
                lgr.warning(
                    "Will not minify web interface javascript, no jsmin available")
                minified = asset.read()                             # no minify available
            with make_tempfile(content=minified) as tempf:          # write minified to tempfile
                js_name = js_file.split('/')[-1]
                ssh.put(tempf, opj(webresources_remote, 'assets', 'js', js_name))  # and upload js

    # explicitly make web+metadata dir of dataset world-readable, if shared set to 'all'
    mode = None
    if shared in (True, 'true', 'all', 'world', 'everybody'):
        mode = 'a+rX'
    elif shared == 'group':
        mode = 'g+rX'
    elif str(shared).startswith('0'):
        mode = shared

    if mode:
        ssh('chmod -R {} {} {}'.format(
            mode,
            sh_quote(dirname(webresources_remote)),
            sh_quote(opj(path, 'index.html'))))
