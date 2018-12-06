import click

from bsm.cmd.base import Base
from bsm.cmd import CmdResult

from bsm.use import Use as BsmUse
from bsm.env import Env

from bsm.config.config_version import ConfigVersion
from bsm.config.config_release import ConfigRelease
from bsm.config.info import Info

from bsm.logger import get_logger
_logger = get_logger()

class Init(Base):
    def execute(self, shell):
        script = self._bsm.shell_init_script(shell)

        self._bsm.default_load()

        return CmdResult(script, script)
