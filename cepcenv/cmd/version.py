import os
import click

from cepcenv import CEPCENV_VERSION

class Version(object):
    def execute(self, config):
        click.echo('cepcenv {0}'.format(CEPCENV_VERSION))
