import os

from bsm.util import which

from bsm.cmd import CmdResult
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

DEFAULT_EDITOR = ['vim', 'vi']

def _detect_editor(editors):
    for editor in editors:
        if which(editor):
            return editor
    return None

class PkgEdit(PkgBase):
    def execute(self, category, subdir, version, package):  # pylint: disable=inconsistent-return-statements
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        pkg_prop_file = pkg_path['prop_file']

        editor = None
        if 'VISUAL' in os.environ:
            editor = os.environ['VISUAL']
        elif 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        else:
            editor = _detect_editor(DEFAULT_EDITOR)

        if not editor:
            _logger.warning(
                'Editor open failed. Please edit the package configuration file by yourself: %s',
                pkg_prop_file)
            return

        _logger.info('Edit package configuration file: %s', pkg_prop_file)
        _logger.debug('Select editor: %s', editor)

        command = [editor, pkg_prop_file]

        return CmdResult(commands={'cmd': command})
