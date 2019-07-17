import copy

from bsm.error import PropPackageParamError

from bsm.prop.packages_base import PackagesBase
from bsm.prop.util import prop_from_file, package_param_from_rel_dir, transform_package
from bsm.prop.util import package_path, expand_package_path, expand_package_env
from bsm.prop.util import install_status, install_step

from bsm.util import walk_rel_dir

from bsm.logger import get_logger
_logger = get_logger()


class PackagesRuntime(PackagesBase):
    def _init_packages(self, handler, prop):
        reinstall = prop['entry'].get('reinstall', False)

        category_runtime = [
            ctg for ctg, prop in prop['category'].items() \
            if prop.get('root') and not prop.get('pre_check')]

        _logger.debug('Category for runtime: %s', category_runtime)

        for category in category_runtime:
            version_dir = prop['category'][category]['version_dir']
            prop_package_dir = prop['category'][category]['prop_package_dir']

            for full_path, rel_dir, f in walk_rel_dir(prop_package_dir):
                if f != prop['app']['prop_package_file']:
                    continue

                try:
                    subdir, package, version = package_param_from_rel_dir(rel_dir, version_dir)
                except PropPackageParamError:
                    continue

                pkg_prop = prop_from_file(full_path)

                pkg_path = package_path(
                    prop['app'], prop['category'], category, subdir, package, version)

                final_pkg_prop = transform_package(
                    handler, 'runtime',
                    category, subdir, package, version, pkg_prop, pkg_path, prop)

                if not version_dir:
                    if 'version' in final_pkg_prop and final_pkg_prop['version']:
                        version = final_pkg_prop['version']
                    else:
                        version = 'unknown'

                self.setdefault(category, {})
                self[category].setdefault(subdir, {})
                self[category][subdir].setdefault(package, {})
                self[category][subdir][package].setdefault(version, {})

                final_props = self[category][subdir][package][version]

                final_props['prop_origin'] = copy.deepcopy(pkg_prop)

                final_props['prop'] = final_pkg_prop
                final_props['prop']['name'] = package
                final_props['prop']['category'] = category
                final_props['prop']['subdir'] = subdir
                final_props['prop']['version'] = version

                final_props['package_path'] = package_path(
                    prop['app'], prop['category'],
                    category, subdir, package, final_props['prop']['version'])
                expand_package_path(
                    final_props['package_path']['main_dir'], final_props['prop'])
                expand_package_env(final_props['prop'])

                final_props['install_status'] = install_status(
                    final_props['package_path']['status_install_file'])

                final_props['step'] = install_step(
                    prop['release_install'], final_props['prop'],
                    final_props['install_status'], reinstall)
