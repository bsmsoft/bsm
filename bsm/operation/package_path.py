from bsm.config.util import package_path

from bsm.operation import Base

class PackagePath(Base):
    def execute(self, package, category, subdir, version):
        return package_path(self._config['app'], self._config['category'], category, subdir, package, version)
