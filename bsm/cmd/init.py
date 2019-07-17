from bsm.shell import Shell

from bsm.cmd import Base
from bsm.cmd import CmdResult

from bsm.logger import get_logger
_logger = get_logger()

class Init(Base):
    def execute(self, no_default, show_script, shell):
        output = ''
        if show_script and shell:
            cmd_name = self._bsm.prop('app')['cmd_name']
            app_root = self._bsm.prop('app').get('app_root', '')

            shell = Shell(shell, cmd_name, app_root)
            shell.add_script('init')
            output = shell.script

        self._bsm.clean()

        if not no_default and 'version' in self._bsm.prop('scenario'):
            self._bsm.load_release()
            self._bsm.load_release_packages()
            _logger.info('software_root : %s', self._bsm.prop('scenario').get('software_root', ''))
            _logger.info('version       : %s', self._bsm.prop('scenario').get('version', ''))

        return CmdResult(output=output, script_types='init')
