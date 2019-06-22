from bsm.cmd.pkg_base import PkgBase

class PkgClean(PkgBase):
    def execute(self, package):
        self._bsm.clean_package(package)
