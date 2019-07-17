from bsm.operation import Base

class PackageExist(Base):
    def execute(self, package, category, subdir, version):
        return self._prop['packages_runtime'].package_exist(package, category, subdir, version)
