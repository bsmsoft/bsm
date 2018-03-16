import click

from bsm import BSM_HOME

class Home(object):
    def execute(self):
        click.echo(BSM_HOME)
