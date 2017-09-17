import click

from cepcenv import CEPCENV_HOME

class Home(object):
    def execute(self, config):
        click.echo(CEPCENV_HOME)
