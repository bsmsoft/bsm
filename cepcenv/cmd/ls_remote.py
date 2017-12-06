import sys
import click

from cepcenv.git import list_remote_tag
from cepcenv.git import GitNotFoundError

class LsRemote(object):
    def execute(self, config, config_version, shell):
        try:
            tags = list_remote_tag(config_version.get('release_repo'))
        except GitNotFoundError as e:
            _logger.fatal('Git is not found. Please install "git" first')
            sys.exit(1)

        versions = [tag[1:] for tag in tags if tag.startswith('v')]

        script = ''
        for version in versions:
            script += shell.echo(version)

        click.echo(script, nl=False)
