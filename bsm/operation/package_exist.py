from bsm.operation import Base

class PackageExist(Base):
    def execute(self, package, category, subdir, version):
        return self._config['package_runtime'].package_exist(package, category, subdir, version)
