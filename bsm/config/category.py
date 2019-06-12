import os

from bsm.config.common import Common

from bsm.util import expand_path

from bsm.logger import get_logger
_logger = get_logger()


class Category(Common):
    def __init__(self, config_entry, config_app, config_env, config_user, config_scenario, config_attribute, config_release):
        super(Category, self).__init__()

        self.__update_category(config_release.get('setting', {}), config_app, config_scenario, config_attribute)

        self.__update_category(config_user, config_app, config_scenario, config_attribute)

        if config_scenario.get('scenario'):
            self.__update_category(config_user.get('scenario', {}).get(config_scenario['scenario'], {}), config_app, config_scenario, config_attribute)

    def __update_category(self, config_container, config_app, config_scenario, config_attribute):
        if 'category' not in config_container:
            return

        for ctg, ctg_cfg in config_container['category'].items():
            if ctg in self:
                _logger.warn('Conflict category: {0}'.format(ctg))
                continue
            self.__load_category(ctg, ctg_cfg, config_app, config_scenario, config_attribute)

    def __load_category(self, ctg, ctg_cfg, config_app, config_scenario, config_attribute):
        self[ctg] = {}
        self[ctg]['name'] = ctg
        self[ctg]['pre_check'] = ctg_cfg.get('pre_check', False)
        self[ctg]['install'] = ctg_cfg.get('install', False)
        self[ctg]['auto_env'] = ctg_cfg.get('auto_env', False)
        self[ctg]['version_dir'] = ctg_cfg.get('version_dir', False)
        self[ctg]['shared'] = ctg_cfg.get('shared', False)

        if 'root' not in ctg_cfg:
            self[ctg]['install'] = False
            self[ctg]['auto_env'] = False
            self[ctg]['shared'] = False
            return

        format_dict = {}
        format_dict.update(config_attribute)
        format_dict.update(config_scenario)
        self[ctg]['root'] = expand_path(ctg_cfg['root'].format(**format_dict))

        self[ctg]['work_dir'] = os.path.join(self[ctg]['root'], config_app['category_work_dir'])
        if self[ctg]['shared']:
            self[ctg]['config_package_dir'] = os.path.join(self[ctg]['work_dir'], 'shared')
        else:
            self[ctg]['config_package_dir'] = os.path.join(self[ctg]['work_dir'], 'release', config_scenario['version'])
        self[ctg]['install_dir'] = os.path.join(self[ctg]['work_dir'], 'install')
