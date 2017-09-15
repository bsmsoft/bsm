import click

class Exit(object):
    def execute(self, config, shell):
        script = ''
        script += shell.undefine_cepcenv()
        script += shell.unset_env('CEPCENV_HOME')

        click.echo(script, nl=False)
