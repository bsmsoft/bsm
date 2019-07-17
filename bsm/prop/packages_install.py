import copy

from bsm.error import PropPackageParamError

from bsm.prop.packages_base import PackagesBase
from bsm.prop.util import package_param_from_identifier, transform_package
from bsm.prop.util import package_path, expand_package_path, expand_package_env
from bsm.prop.util import install_status, install_step

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class PackagesInstall(PackagesBase):
    def _init_packages(self, handler, prop):
        reinstall = prop['entry'].get('reinstall', False)

        category_install = [
            ctg for ctg, ctg_prop in prop['category'].items() if ctg_prop['install']]

        _logger.debug('Category for install: %s', category_install)

        for identifier, pkg_prop in prop['release_package'].items():
            try:
                category_name, subdir, pkg_name = package_param_from_identifier(identifier,
                                                                                pkg_prop)
            except PropPackageParamError:
                continue

            if category_name not in category_install:
                _logger.debug(
                    'Package "%s" could not be installed with category "%s"',
                    pkg_name, category_name)
                continue

            version = ensure_list(pkg_prop.get('version', []))

            version_dir = prop['category'][category_name]['version_dir']
            if (not version_dir) and len(version) > 1:
                _logger.warning(
                    'Only one version could be installed when category version_dir is false')
                version = version[:1]

            if not version:
                _logger.warning(
                    'No version is specified for category "%s", package "%s"',
                    category_name, pkg_name)

            for ver in version:
                self.setdefault(category_name, {})
                self[category_name].setdefault(subdir, {})
                self[category_name][subdir].setdefault(pkg_name, {})
                if ver in self[category_name][subdir][pkg_name]:
                    _logger.warning(
                        'Duplicated package found: '
                        'category "%s", subdir "%s", package "%s", version "%s"',
                        category_name, subdir, pkg_name, ver)
                self[category_name][subdir][pkg_name].setdefault(ver, {})
                final_props = self[category_name][subdir][pkg_name][ver]

                final_props['prop_origin'] = copy.deepcopy(pkg_prop)
                final_props['prop_origin']['version'] = ver

                pkg_path = package_path(
                    prop['app'], prop['category'], category_name, subdir, pkg_name, ver)

                final_props['prop'] = transform_package(
                    handler, 'install',
                    category_name, subdir, pkg_name, ver, pkg_prop, pkg_path, prop)
                final_props['prop']['name'] = pkg_name
                final_props['prop']['category'] = category_name
                final_props['prop']['subdir'] = subdir
                if 'version' not in final_props['prop']:
                    final_props['prop']['version'] = ver

                final_props['package_path'] = package_path(
                    prop['app'], prop['category'],
                    category_name, subdir, pkg_name, final_props['prop']['version'])
                expand_package_path(
                    final_props['package_path']['main_dir'], final_props['prop'])
                expand_package_env(final_props['prop'])

                final_props['install_status'] = install_status(
                    final_props['package_path']['status_install_file'])

                final_props['step'] = install_step(
                    prop['release_install'], final_props['prop'],
                    final_props['install_status'], reinstall)
