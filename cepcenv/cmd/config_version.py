import os
import click

from cepcenv.config.util import dump_config_str

class ConfigVersion(object):
    def execute(self, config, version_config, release_config):
        click.echo(dump_config_str(version_config))
        click.echo(dump_config_str(release_config))
