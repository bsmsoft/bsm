import re

from bsm.operation import Base

from bsm.git import Git
from bsm.git import GitNotFoundError
from bsm.git import GitEmptyUrlError

from bsm.logger import get_logger
_logger = get_logger()

class LsRemote(Base):
    def execute(self, list_all):
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

        if list_all:
            version_pattern_string = self._config['app']['version_pattern']
        else:
            version_pattern_string = self._config['app']['version_stable_pattern']

        version_pattern = re.compile(version_pattern_string)
        versions = {}
        for tag in tags:
            m = version_pattern.match(tag)
            if not m:
                continue
            groups = m.groups()
            if len(groups) == 0:
                continue
            version = groups[0]
            if version in versions:
                _logger.warn('Duplicated version "{0}" found, please check the version pattern "{1}"'.format(version, version_pattern_string))
                continue

            versions[version] = tag

        return versions
