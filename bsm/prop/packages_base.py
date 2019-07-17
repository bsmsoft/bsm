from bsm.handler import Handler

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.error import PropPackageError

from bsm.prop.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class PackagesBase(CommonDict):
    def __init__(self, prop):
        super(PackagesBase, self).__init__()

        with Handler(prop['release_path']['handler_python_dir']) as h:
            self._init_packages(h, prop)     # pylint: disable=no-member

    def package_exist(self, category, subdir, name, version):
        return (category in self and subdir in self[category] and
                name in self[category][subdir] and version in self[category][subdir][name])

    def package_props(self, category, subdir, name, version):
        if not self.package_exist(category, subdir, name, version):
            _logger.error('Package not found: %s.%s.%s.%s', category, name, subdir, version)
            raise PropPackageError
        return self[category][subdir][name][version]

    def save_install_status(self, category, subdir, name, version):
        pkg_install_props = self.package_props(category, subdir, name, version)
        safe_mkdir(pkg_install_props['package_path']['status_dir'])
        dump_config(pkg_install_props['install_status'],
                    pkg_install_props['package_path']['status_install_file'])

    def save_package_prop(self, category, subdir, name, version):
        pkg_install_props = self.package_props(category, subdir, name, version)
        safe_mkdir(pkg_install_props['package_path']['prop_dir'])
        dump_config(pkg_install_props['prop_origin'],
                    pkg_install_props['package_path']['prop_file'])
