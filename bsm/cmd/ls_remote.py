import sys
import click

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

from bsm.logger import get_logger
_logger = get_logger()

class LsRemote(object):
    def execute(self, config, config_version):
        try:
            git = Git()
            tags = git.ls_remote_tags(config_version.get('release_repo'))
        except GitNotFoundError:
            _logger.error('Git is not found. Please install "git" first')
            raise
        except GitEmptyUrlError:
            _logger.error('No release repository found. Please setup "release_repo" in "$HOME/.bsm.conf" first')
            raise

        versions = [tag[1:] for tag in tags if tag.startswith('v')]
        versions.sort()


        release_repo = config_version.get('release_repo')
        click.echo('(Release repository: "{0}")'.format(release_repo))

        for version in versions:
            click.echo(version)
