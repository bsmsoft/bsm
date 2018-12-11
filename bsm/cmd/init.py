from bsm.cmd.base import Base
from bsm.cmd import CmdResult
from bsm.shell import Shell

class Init(Base):
    def execute(self, shell):
        cmd_name = self._bsm.config('app')['cmd_name']
        app_root = self._bsm.config('app').get('app_root', '')

        shell = Shell(shell, cmd_name, app_root)
        shell.add_script('init')

#        self._bsm.default_load()

        return CmdResult(shell.script, 'init')
