from bsm.cmd import Base

class PkgClean(Base):
    def execute(self, package):
        self._bsm.clean_package(package)
        return ''
