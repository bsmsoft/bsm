import copy

from bsm.error import OperationInstallPackagePropError

from bsm.prop.util import package_path
from bsm.prop.util import check_conflict_package

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackageProp(Base):
    def execute(self, package, category, subdir, version,
                category_origin, subdir_origin, version_origin, from_install=False):
        prop_packages_name = 'packages_install' if from_install else 'packages_runtime'

        pkg_prop_origin = copy.deepcopy(
            self._prop[prop_packages_name].package_props(
                category_origin, subdir_origin, package, version_origin)['prop_origin'])
        pkg_prop_origin['version'] = version

        pkg_path = package_path(self._prop['app'], self._prop['category'],
                                category, subdir, package, version)

        ctg_cf, subd_cf, pkg_cf, ver_cf = check_conflict_package(
            pkg_path['main_dir'], self._prop['packages_runtime'])
        if ctg_cf:
            raise OperationInstallPackagePropError(
                'Package path conflicts with package "{0}", '
                'category "{1}", subdir "{2}", version "{3}"'
                .format(pkg_cf, ctg_cf, subd_cf, ver_cf))

        safe_mkdir(pkg_path['prop_dir'])
        dump_config(pkg_prop_origin, pkg_path['prop_file'])

        self._prop.reset()
