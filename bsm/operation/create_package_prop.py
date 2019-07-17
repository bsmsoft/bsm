import os

from bsm.error import OperationCreatePackagePropError

from bsm.prop.util import package_path
from bsm.prop.util import check_conflict_package

from bsm.util import safe_mkdir

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class CreatePackageProp(Base):
    def execute(self, package, category, subdir, version):
        pkg_path = package_path(
            self._prop['app'], self._prop['category'], category, subdir, package, version)

        ctg_cf, subd_cf, pkg_cf, ver_cf = check_conflict_package(
            pkg_path['main_dir'], self._prop['packages_runtime'])
        if ctg_cf:
            raise OperationCreatePackagePropError(
                'Package path conflicts with package "{0}", '
                'category "{1}", subdir "{2}", version "{3}"'
                .format(pkg_cf, ctg_cf, subd_cf, ver_cf))

        safe_mkdir(pkg_path['prop_dir'])

        if not os.path.exists(pkg_path['prop_file']):
            open(pkg_path['prop_file'], 'w').close()

        self._prop.reset()
