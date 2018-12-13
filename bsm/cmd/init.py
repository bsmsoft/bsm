from bsm.cmd import Base
from bsm.cmd import CmdResult
from bsm.shell import Shell

class Init(Base):
    def execute(self, show_script, shell):
        output = ''
        if show_script and shell:
            cmd_name = self._bsm.config('app')['cmd_name']
            app_root = self._bsm.config('app').get('app_root', '')

            shell = Shell(shell, cmd_name, app_root)
            shell.add_script('init')
            output = shell.script

#        self._bsm.default_load()

        return CmdResult(output, 'init')
