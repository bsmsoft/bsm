from bsm.operation import Base

class PackageProps(Base):
    def execute(self, package, category, subdir, version):
        return self._prop['packages_runtime'].package_props(category, subdir, package, version)
