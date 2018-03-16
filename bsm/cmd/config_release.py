import os
import click

from bsm.config import dump_config_str

class ConfigRelease(object):
    def execute(self, config_release):
        click.echo(dump_config_str(config_release.config), nl=False)
