from bsm.shell import Shell

from bsm.cmd import Base

class Setup(Base):
    def execute(self, shell):
        cmd_name = self._bsm.prop('app')['cmd_name']
        app_root = self._bsm.prop('app').get('app_root', '')

        shell = Shell(shell, cmd_name, app_root)
        return shell.setup_script()
