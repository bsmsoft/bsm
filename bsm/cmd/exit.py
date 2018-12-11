from bsm.cmd import Base
from bsm.cmd import CmdResult
from bsm.shell import Shell

class Exit(Base):
    def execute(self, shell):
        output = ''
        if shell and self._output_format != 'plain':
            cmd_name = self._bsm.config('app')['cmd_name']
            app_root = self._bsm.config('app').get('app_root', '')

            shell = Shell(shell, cmd_name, app_root)
            shell.add_script('exit')
            output = shell.script

#        self._bsm.clean()

        return CmdResult(output, 'exit')
