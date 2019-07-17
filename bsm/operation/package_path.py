from bsm.prop.util import package_path

from bsm.operation import Base

class PackagePath(Base):
    def execute(self, package, category, subdir, version):
        return package_path(self._prop['app'], self._prop['category'],
                            category, subdir, package, version)
