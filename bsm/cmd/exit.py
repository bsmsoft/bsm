from bsm.cmd.base import Base
from bsm.cmd import CmdResult
from bsm.shell import Shell

class Exit(Base):
    def execute(self, shell):
        if not shell:
            return ''

        cmd_name = self._bsm.config('app')['cmd_name']
        app_root = self._bsm.config('app').get('app_root', '')

        shell = Shell(shell, cmd_name, app_root)
        shell.add_script('exit')

#        self._bsm.clean()

        return CmdResult(shell.script, 'exit')
