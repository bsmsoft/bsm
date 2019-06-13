import os
from collections import OrderedDict

from bsm.config.common import Common

from bsm.util import ensure_list
from bsm.util import expand_path

from bsm.logger import get_logger
_logger = get_logger()


class Category(Common):
    def __init__(self, config_entry, config_app, config_env, config_user, config_scenario, config_attribute, config_release):
        super(Category, self).__init__()

        self['content'] = {}
        self['priority'] = []

        self.__update_content(config_release.get('setting', {}), config_app, config_scenario, config_attribute)

        self.__update_content(config_user, config_app, config_scenario, config_attribute)

        if config_scenario.get('scenario'):
            self.__update_content(config_user.get('scenario', {}).get(config_scenario['scenario'], {}), config_app, config_scenario, config_attribute)

        # Remove duplicated
        self['priority'] = list(OrderedDict.fromkeys(self['priority']))

    def __update_content(self, config_container, config_app, config_scenario, config_attribute):
        self.__update_category(config_container, config_app, config_scenario, config_attribute)
        self.__update_priority(config_container)

    def __update_category(self, config_container, config_app, config_scenario, config_attribute):
        if 'category' not in config_container:
            return

        for ctg, ctg_cfg in config_container['category'].items():
            if ctg in self:
                _logger.warn('Conflicting category: {0}'.format(ctg))
            self.__load_category(ctg, ctg_cfg, config_app, config_scenario, config_attribute)

    def __load_category(self, ctg, ctg_cfg, config_app, config_scenario, config_attribute):
        self['content'][ctg] = {}
        result = self['content'][ctg]

        result['name'] = ctg
        result['pre_check'] = ctg_cfg.get('pre_check', False)
        result['install'] = ctg_cfg.get('install', False)
        result['auto_env'] = ctg_cfg.get('auto_env', False)
        result['version_dir'] = ctg_cfg.get('version_dir', False)
        result['shared'] = ctg_cfg.get('shared', False)

        if 'root' not in ctg_cfg:
            result['install'] = False
            result['auto_env'] = False
            result['shared'] = False
            return

        format_dict = {}
        format_dict.update(config_attribute)
        format_dict.update(config_scenario)
        result['root'] = expand_path(ctg_cfg['root'].format(**format_dict))

        result['work_dir'] = os.path.join(result['root'], config_app['category_work_dir'])
        if result['shared']:
            result['config_package_dir'] = os.path.join(result['work_dir'], 'shared')
        else:
            result['config_package_dir'] = os.path.join(result['work_dir'], 'release', config_scenario['version'])
        result['install_dir'] = os.path.join(result['work_dir'], 'install')

    def __update_priority(self, config_container):
        priority = ensure_list(config_container.get('category_priority', []))
        priority = [ctg for ctg in priority if ctg in self['content']]
        priority += [ctg for ctg in config_container.get('category', {}) if ctg not in priority]
        self['priority'] = priority + self['priority']
