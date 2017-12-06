import click

from cepcenv.env import Env

class LsPackage(object):
    def execute(self, config, config_version):
        env = Env()

        for name, info in env.package_info.items():
            click.echo('{name} @ {version} : {category} - {path}'.format(name=name, **info))
