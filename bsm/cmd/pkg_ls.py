from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

class PkgLs(PkgBase):
    def execute(self, list_all, package):
        self._check_release()

        if list_all:
            packages = self._bsm.ls_all_package()
        else:
            packages = self._bsm.ls_active_package()

        if package:
            if package not in packages:
                raise CmdError('Package "{0}" is not found'.format(package))
            return packages[package]

        return packages
