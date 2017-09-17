import click

class Init(object):
    def execute(self, config, shell):
        script = ''
        script += shell.define_cepcenv()

        click.echo(script, nl=False)
