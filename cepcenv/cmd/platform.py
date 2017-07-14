import click

from cepcenv.cmd.cmdcommon import CmdCommon
from cepcenv.software_platform import SoftwarePlatform


class Platform(CmdCommon):
    def execute(self):
        sp = SoftwarePlatform(self._config())
        click.echo(sp.all())
