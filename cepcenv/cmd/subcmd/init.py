import click

from cepcenv import CEPCENV_HOME

from cepcenv.cmd.cmdcommon import CmdCommon


class Init(CmdCommon):
    def execute(self):
        shell = self._shell()

        script = ''
        script += shell.set_env('CEPCENV_HOME', CEPCENV_HOME)
        script += shell.define_cepcenv()

        click.echo(script, nl=False)
