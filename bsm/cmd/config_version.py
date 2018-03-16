import os
import click

from bsm.config import dump_config_str

class ConfigVersion(object):
    def execute(self, config_version):
        click.echo(dump_config_str(config_version.config), nl=False)
