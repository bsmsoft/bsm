import os
import click

from cepcenv import CEPCENV_HOME

class Version(object):
    def execute(self, config):
        with open(os.path.join(CEPCENV_HOME, 'CEPCENV_VERSION'), 'r') as f:
            ver = f.read()
        click.echo('cepcenv {0}'.format(ver.strip()))
