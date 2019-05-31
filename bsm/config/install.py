import os
import sys
import copy

from bsm.config.common import Common

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class ConfigInstallStepError(Exception):
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


class Install(Common):
    def load(self, config_app, config_scenario, config_release_path, config_attribute, config_release, config_category):
        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config install')
            return

        category_priority = config_release.get('setting', {}).get('category_priority', [])

        category_install = []
        for ctg, ctg_cfg in config_category.items():
            if ctg_cfg['install']:
                category_install.append(ctg)

        self.__load_install_setting(config_release)

        sys.path.insert(0, config_release_path['handler_python_dir'])

        config_release_package = config_release.get('package', {})
        for identifier, pkg_cfg in config_release_package.items():
            frag = identifier.split(os.sep)

            if 'category' in pkg_cfg:
                category_name = pkg_cfg['category']
            elif len(frag) > 1:
                category_name = frag[0]
            else:
                _logger.warn('Category not specified for {0}'.format(identifier))
                continue

            if category_name not in category_install:
                continue

            if 'name' in pkg_cfg:
                pkg_name = pkg_cfg['name']
            elif frag[-1]:
                pkg_name = frag[-1]
            else:
                _logger.error('Package name not found for {0}'.format(identifier))
                continue

            if pkg_name in self:
                _logger.debug('Duplicated package name found: {0}'.format(pkg_name))
                if category_name not in category_priority:
                    continue
                if self[pkg_name]['category'] in category_priority:
                    index_new = category_priority.index(category_name)
                    index_old = category_priority.index(self[pkg_name]['category'])
                    if index_new >= index_old:
                        continue

            self[pkg_name] = {}
            self[pkg_name]['category'] = category_name
            self[pkg_name]['identifier'] = identifier

            self[pkg_name]['config'] = self.__transform_package(pkg_name, category_name, pkg_cfg,
                    config_app, config_scenario, config_release_path, config_attribute, config_release, config_category)

            self[pkg_name]['step'] = self.__install_step(self[pkg_name]['config'])

        sys.path.remove(config_release_path['handler_python_dir'])

    def __load_install_setting(self, config_release):
        setting_install = config_release.get('setting', {}).get('install', {})
        self.__all_steps = setting_install.get('steps', [])
        self.__atomic_start = setting_install.get('atomic_start')
        self.__atomic_end = setting_install.get('atomic_end')
        self.__no_skip = ensure_list(setting_install.get('no_skip', []))

        if len(self.__all_steps) != len(set(self.__all_steps)):
            raise ConfigInstallStepError('Duplicated steps found: {0}'.format(self.__all_steps))

        if self.__atomic_start not in self.__all_steps or self.__atomic_end not in self.__all_steps:
            raise ConfigInstallStepError('Can not find atomic start/end: {0}/{1}'.format(self.__atomic_start, self.__atomic_end))

        if self.__all_steps.index(self.__atomic_start) > self.__all_steps.index(self.__atomic_end):
            raise ConfigInstallStepError('atomic_start should not be after atomic_end')

    def __transform_package(self, name, category, pkg_cfg,
            config_app, config_scenario, config_release_path, config_attribute, config_release, config_category):
        param = {}
        param['operation'] = 'install'
        param['name'] = name
        param['category'] = category
        param['package'] = copy.deepcopy(pkg_cfg)
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

    def __install_step(self, pkg_cfg):
        result = []

        for action in self.__all_steps:
            if not pkg_cfg.get('install', {}).get(action):
                continue

            if action not in self.__no_skip and pkg_mgr.is_finished(pkg, action):
                continue

            config_action = ensure_list(pkg_info['config']['install'][action])

            sub_index = 0
            for cfg_action in config_action:
                handler, param = _step_param(cfg_action)
                if handler:
                    result.append({'action': action, 'sub_action': sub_index, 'handler': handler, 'param': param})
                sub_index += 1
