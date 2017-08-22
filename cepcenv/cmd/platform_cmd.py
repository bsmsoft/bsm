import click

from cepcenv.software_platform import SoftwarePlatform

class PlatformCmd(object):
    def execute(self, config, scenario_config):
        click.echo(scenario_config['platform'])
