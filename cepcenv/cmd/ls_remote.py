import sys
import click

from cepcenv.git import Git
from cepcenv.git import GitNotFoundError

from cepcenv.logger import get_logger
_logger = get_logger()

class LsRemote(object):
    def execute(self, config, config_version):
        try:
            git = Git()
            tags = git.ls_remote_tags(config_version.get('release_repo'))
        except GitNotFoundError as e:
            _logger.fatal('Git is not found. Please install "git" first')
            sys.exit(1)

        versions = [tag[1:] for tag in tags if tag.startswith('v')]
        versions.sort()


        release_repo = config_version.get('release_repo')
        click.echo('(Release repository: "{0}")'.format(release_repo))

        for version in versions:
            click.echo(version)
