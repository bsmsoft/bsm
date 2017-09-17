import click

class Exit(object):
    def execute(self, config, shell):
        script = ''
        script += shell.undefine_cepcenv()

        click.echo(script, nl=False)
