from bsm.operation.base import Base

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

class LsRemote(Base):
    def execute(self):
        try:
            git = Git()
            tags = git.ls_remote_tags(self._config['scenario']['release_repo'])
        except GitNotFoundError:
            _logger.error('Git is not found. Please install "git" first')
            raise
        except GitEmptyUrlError:
            _logger.error('No release repository found. Please setup "release_repo" first')
            raise

        versions = [tag[1:] for tag in tags if tag.startswith(b'v')]
        versions.sort()

        return versions
