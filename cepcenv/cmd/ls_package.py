import click

from cepcenv.env import Env

class LsPackage(object):
    def execute(self, config, config_version, shell):
        script = ''

        env = Env()

        for name, info in env.package_info.items():
            script += shell.echo('{name} @ {version} : {category} - {path}'.format(name=name, **info))

        click.echo(script, nl=False)
