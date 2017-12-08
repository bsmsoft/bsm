import sys
import click

from cepcenv.git import list_remote_tag
from cepcenv.git import GitNotFoundError

from cepcenv.logger import get_logger
_logger = get_logger()

class LsRemote(object):
    def execute(self, config, config_version):
        try:
            tags = list_remote_tag(config_version.get('release_repo'))
        except GitNotFoundError as e:
            _logger.fatal('Git is not found. Please install "git" first')
            sys.exit(1)

        versions = [tag[1:] for tag in tags if tag.startswith('v')]

        for version in versions:
            click.echo(version)
