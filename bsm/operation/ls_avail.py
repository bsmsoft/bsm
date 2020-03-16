from bsm.operation import Base
from bsm.operation.util import list_versions

from bsm.git import Git

from bsm.logger import get_logger
_logger = get_logger()


class LsAvail(Base):
    def execute(self, list_all):
        release_repo = self._prop['scenario']['release_repo']

        if list_all:
            version_pattern = self._prop['app']['version_pattern']
        else:
            version_pattern = self._prop['app']['version_stable_pattern']

        git = Git(git_temp=self._prop['app'].get('git_temp'))

        return list_versions(release_repo, version_pattern, git)
