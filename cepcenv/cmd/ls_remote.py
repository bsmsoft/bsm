import functools
import click

from cepcenv.git import list_remote_tag

class LsRemote(object):
    def execute(self, config, version_config, release_config, shell):
        tags = list_remote_tag(version_config['release_repo'])
        versions = [tag[1:] for tag in tags if tag.startswith('v')]

        script = ''
        for version in versions:
            script += shell.echo(version)

        click.echo(script, nl=False)
