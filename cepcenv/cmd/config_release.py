import os
import click

from cepcenv.config import dump_config_str

class ConfigRelease(object):
    def execute(self, config, config_release):
        click.echo(dump_config_str(config_release.config), nl=False)
