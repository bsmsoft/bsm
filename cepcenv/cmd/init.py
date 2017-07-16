import click

from cepcenv import CEPCENV_HOME

class Init(object):
    def execute(self, config, shell):
        script = ''
        script += shell.set_env('CEPCENV_HOME', CEPCENV_HOME)
        script += shell.define_cepcenv()

        click.echo(script, nl=False)
