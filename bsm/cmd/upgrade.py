import sys

from bsm.cmd import CmdResult
from bsm.cmd import Base

class Upgrade(Base):
    def execute(self):      # pylint: disable=no-self-use
        def pip_install_cmd(package):
            return [sys.executable, '-m', 'pip', 'install', '--upgrade', package]

        commands = []
        commands.append({'cmd': pip_install_cmd('pip')})
        commands.append({'cmd': pip_install_cmd('bsm')})

        return CmdResult(commands=commands)
