import os
import subprocess

from bsm.util import which

from bsm.cmd import Base
from bsm.cmd import CmdResult
from bsm.cmd import CmdError

from bsm.logger import get_logger
_logger = get_logger()

DEFAULT_EDITOR = ['vim', 'vi']

def _detect_editor(editors):
    for editor in editors:
        if which(editor):
            return editor
    return None

class PkgEdit(Base):
    def execute(self, category, subdir, version, package):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        pkg_cfg_file = pkg_path['config_file']

        editor = None
        if 'VISUAL' in os.environ:
            editor = os.environ['VISUAL']
        elif 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        else:
            editor = _detect_editor(DEFAULT_EDITOR)

        if not editor:
            _logger.warn('Editor open failed. Please edit the package configuration file by yourself: {0}'.format(pkg_cfg_file))
            return ''

        _logger.info('Edit package configuration file: {0}'.format(pkg_cfg_file))
        _logger.debug('Select editor: {0}'.format(editor))

        command = [editor, pkg_cfg_file]

        return CmdResult(commands=command)
