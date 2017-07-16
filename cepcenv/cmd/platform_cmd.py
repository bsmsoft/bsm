import click

from cepcenv.software_platform import SoftwarePlatform

class PlatformCmd(object):
    def execute(self, config):
        sp = SoftwarePlatform(config)
        click.echo(sp.all())
