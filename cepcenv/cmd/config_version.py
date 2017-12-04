import os
import click

from cepcenv.config import dump_config_str

class ConfigVersion(object):
    def execute(self, config, config_version):
        click.echo(dump_config_str(config_version.config), nl=False)
