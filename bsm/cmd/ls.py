from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Ls(Base):
    def execute(self):
        local_versions = self._bsm.ls_release_version()

        if self._output_format != 'plain':
            return local_versions

        current_release = self._bsm.current()

        result_lines = []
        for version in local_versions:
            if version == current_release.get('release_version'):
                result_lines.append('* {0}'.format(version))
            else:
                result_lines.append('  {0}'.format(version))

        return result_lines
