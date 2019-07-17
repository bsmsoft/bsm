from bsm.prop.util import find_package

from bsm.handler import Handler

from bsm.operation import Base

class FindPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None, from_install=False):
        prop_packages_name = 'packages_install' if from_install else 'packages_runtime'

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            return find_package(h, self._prop['category_priority'], self._prop[prop_packages_name],
                                package, category, subdir, version)
