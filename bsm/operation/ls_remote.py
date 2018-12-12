import re

from bsm.operation import Base

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

from bsm.logger import get_logger
_logger = get_logger()

class LsRemote(Base):
    def execute(self):
        try:
            if 'git_temp' in self._config['app']:
                git = Git(git_temp=self._config['app']['git_temp'])
            else:
                git = Git()
            tags = git.ls_remote_tags(self._config['scenario']['release_repo'])
        except GitNotFoundError:
            _logger.error('Git is not found. Please install "git" first')
            raise
        except GitEmptyUrlError:
            _logger.error('No release repository found. Please setup "release_repo" first')
            raise

        versions = []
        version_pattern = re.compile(self._config['app']['version_pattern'])
        for tag in tags:
            m = version_pattern.match(tag)
            if not m:
                continue
            groups = m.groups()
            if len(groups) > 0:
                versions.append(groups[0])

        versions.sort()

        return versions
