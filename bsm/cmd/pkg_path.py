from bsm.cmd import Base
from bsm.cmd import CmdError

class PkgPath(Base):
    def execute(self, category, subdir, version, package):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

        return self._bsm.package_path(package, category, subdir, version)