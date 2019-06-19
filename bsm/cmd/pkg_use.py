from bsm.cmd import Base
from bsm.cmd import CmdError

class PkgUse(Base):
    def execute(self, category, subdir, version, package):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

        ctg, sd, ver = self._bsm.use_package(package, category, subdir, version)
        return ctg, sd, ver
