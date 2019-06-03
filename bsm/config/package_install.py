import os
import sys
import copy

from bsm.config.common import Common

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util import is_str
from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class ConfigPackageInstallStepError(Exception):
    pass


def _step_param(config_action):
    if not config_action:
        return None, None

    if is_str(config_action):
        return config_action, None

    if isinstance(config_action, dict):
        if len(config_action) > 1:
            _logger.warn('More than one actions found in the install action dictionary. Will only randomly choose one!')
            _logger.debug('config_action: {0}'.format(config_action))
        handler = next(iter(config_action))
        return handler, config_action[handler]

    return None, None


class PackageInstall(Common):
    def load(self, config_app, config_scenario, config_release_path, config_attribute, config_release, config_category):
        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config install')
            return

        category_install = [ctg for ctg, ctg_cfg in config_category.items() if ctg_cfg['install']]

        self.__load_install_setting(config_release)

        sys.path.insert(0, config_release_path['handler_python_dir'])

        config_release_package = config_release.get('package', {})
        for identifier, pkg_cfg in config_release_package.items():
            frag = identifier.split(os.sep)

            # Use the first part as default category name
            if 'category' in pkg_cfg:
                category_name = pkg_cfg['category']
            elif len(frag) > 1:
                category_name = frag[0]
            else:
                _logger.warn('Category not specified for {0}'.format(identifier))
                continue

            if category_name not in category_install:
                continue

            # Use the last part as default package name
            if 'name' in pkg_cfg:
                pkg_name = pkg_cfg['name']
            elif frag[-1]:
                pkg_name = frag[-1]
            else:
                _logger.error('Package name not found for {0}'.format(identifier))
                continue

            # Use the middle part as default subdir
            if 'subdir' in pkg_cfg:
                subdir = pkg_cfg['subdir']
            elif frag[1:-1]:
                subdir = os.path.join(*frag[1:-1])
            else:
                subdir = ''

            version = ensure_list(pkg_cfg.get('version', []))

            version_dir = config_category[category_name]['version_dir']
            if (not version_dir) and len(version) > 1:
                _logger.warn('Only one version could be installed when category version_dir is false')
                version = version[:1]

            if not version:
                _logger.warn('No version is specified for category({0}), package({1})'.format(category_name, pkg_name))

            for ver in version:
                self.setdefault(category_name, {})
                self[category_name].setdefault(subdir, {})
                self[category_name][subdir].setdefault(pkg_name, {})
                if version_dir:
                    self[category_name][subdir][pkg_name].setdefault(ver, {})
                    if ver in self[category_name][subdir][pkg_name]:
                        _logger.warn('Duplicated package found: category({0}), subdir({1}), package({2}), version({3})'.format(category_name, subdir, pkg_name, ver))
                    final_config = self[category_name][subdir][pkg_name][ver]
                else:
                    if pkg_name in self[category_name][subdir]:
                        _logger.warn('Duplicated package found: category({0}), subdir({1}), package({2})'.format(category_name, subdir, pkg_name))
                    final_config = self[category_name][subdir][pkg_name]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)
                final_config['config_origin']['version'] = ver

                final_config['config'] = self.__transform_package(category_name, pkg_name, subdir, ver, pkg_cfg,
                        config_app, config_scenario, config_release_path, config_attribute, config_release, config_category)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name
                final_config['config']['subdir'] = subdir
                final_config['config']['version'] = ver

                final_config['package_path'] = self.__package_path(config_category, final_config['config'])
                final_config['install_path'] = self.__install_path(config_category, final_config['config'])

                final_config['step'] = self.__install_step(final_config['config'])

        sys.path.remove(config_release_path['handler_python_dir'])

    def __transform_package(self, category, name, subdir, version, pkg_cfg,
            config_app, config_scenario, config_release_path, config_attribute, config_release, config_category):
        param = {}
        param['operation'] = 'install'

        param['name'] = name
        param['category'] = category
        param['subdir'] = subdir
        param['version'] = version

        param['config_package'] = copy.deepcopy(pkg_cfg)
        param['config_app'] = config_app.data_copy
        param['config_scenario'] = config_scenario.data_copy
        param['config_release_path'] = config_release_path.data_copy
        param['config_attribute'] = config_attribute.data_copy
        param['config_release'] = config_release.data_copy
        param['config_category'] = config_category.data_copy

        try:
            with Handler() as h:
                result = h.run('transform_package', param)
                if isinstance(result, dict):
                    return result
        except HandlerNotFoundError as e:
            _logger.debug('Transformer for package not found: {0}'.format(e))

        return copy.deepcopy(pkg_cfg)

    def __package_path(self, config_category, pkg_cfg):
        package_path = {}
        ctg_cfg = config_category[pkg_cfg['category']]
        if ctg_cfg['version_dir']:
            package_path['main_dir'] = os.path.join(ctg_cfg['root'], pkg_cfg['subdir'], pkg_cfg['name'], pkg_cfg['version'])
            package_path['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'versions', pkg_cfg['version'])
        else:
            package_path['main_dir'] = os.path.join(ctg_cfg['root'], pkg_cfg['subdir'], pkg_cfg['name'])
            package_path['config_dir'] = os.path.join(ctg_cfg['config_package_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'head')
        package_path['config_file'] = os.path.join(package_path['config_dir'], 'package.yml')
        return package_path

    def __install_path(self, config_category, pkg_cfg):
        install_path = {}
        ctg_cfg = config_category[pkg_cfg['category']]
        if ctg_cfg['version_dir']:
            install_path['work_dir'] = os.path.join(ctg_cfg['install_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'versions', pkg_cfg['version'])
        else:
            install_path['work_dir'] = os.path.join(ctg_cfg['install_dir'], pkg_cfg['subdir'], pkg_cfg['name'], 'head')
        install_path['temp_dir'] = os.path.join(ctg_cfg['work_dir'], 'temp')
        install_path['status_dir'] = os.path.join(ctg_cfg['work_dir'], 'status')
        install_path['log_dir'] = os.path.join(ctg_cfg['work_dir'], 'log')
        return install_path

    def __load_install_setting(self, config_release):
        setting_install = config_release.get('setting', {}).get('install', {})
        self.__all_steps = setting_install.get('steps', [])
        self.__atomic_start = setting_install.get('atomic_start')
        self.__atomic_end = setting_install.get('atomic_end')

        if len(self.__all_steps) != len(set(self.__all_steps)):
            raise ConfigInstallStepError('Duplicated steps found: {0}'.format(self.__all_steps))

        if self.__atomic_start not in self.__all_steps or self.__atomic_end not in self.__all_steps:
            raise ConfigInstallStepError('Can not find atomic start/end: {0}/{1}'.format(self.__atomic_start, self.__atomic_end))

        if self.__all_steps.index(self.__atomic_start) > self.__all_steps.index(self.__atomic_end):
            raise ConfigInstallStepError('atomic_start should not be after atomic_end')

    def __install_step(self, pkg_cfg):
        result = []

        for action in self.__all_steps:
            config_action = ensure_list(pkg_cfg.get('install', {}).get(action, []))

            sub_index = 0
            for cfg_action in config_action:
                handler, param = _step_param(cfg_action)
                if handler:
                    result.append({'action': action, 'sub_action': sub_index, 'handler': handler, 'param': param})
                    sub_index += 1

            if sub_index == 0:
                result.append({'action': action, 'sub_action': sub_index, 'handler': '', 'param': {}})

        return result
