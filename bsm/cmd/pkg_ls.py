from bsm.cmd import Base
from bsm.cmd import CmdError

class PkgLs(Base):
    def execute(self, list_all, package):
        if list_all:
            packages = self._bsm.ls_all_package()
        else:
            packages = self._bsm.ls_active_package()

        if package:
            if package not in packages:
                raise CmdError('Package "{0}" is not found'.format(package))
            return packages[package]

        return packages
