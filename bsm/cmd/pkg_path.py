from bsm.cmd import Base
from bsm.cmd import CmdError

class PkgPath(Base):
    def execute(self, category, subdir, version, list_all, package):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

        pkg_path = self._bsm.package_path(package, category, subdir, version)

        if not list_all:
            return pkg_path['main_dir']

        return pkg_path
