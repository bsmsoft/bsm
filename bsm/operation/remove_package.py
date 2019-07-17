from bsm.util import safe_rmdir

from bsm.prop.util import package_path

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class RemovePackage(Base):
    def execute(self, package, category, subdir, version):
        pkg_path = package_path(
            self._prop['app'], self._prop['category'], category, subdir, package, version)

        safe_rmdir(pkg_path['prop_dir'])
        safe_rmdir(pkg_path['work_dir'])
