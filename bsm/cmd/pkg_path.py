from bsm.cmd import Base

class PkgPath(Base):
    def execute(self, category, subdir, version, package):
        return self._bsm.package_path(package, category, subdir, version)
