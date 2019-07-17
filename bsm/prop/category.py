import os

from bsm.prop.common_dict import CommonDict

from bsm.util import expand_path

from bsm.error import PropCategoryError

from bsm.logger import get_logger
_logger = get_logger()


class Category(CommonDict):
    def __init__(self, prop):
        super(Category, self).__init__()

        self.__update_category(
            prop['release_setting'], prop['app'], prop['scenario'], prop['attribute'])

        self.__update_category(
            prop['user'], prop['app'], prop['scenario'], prop['attribute'])

        if prop['scenario'].get('scenario'):
            self.__update_category(
                prop['user'].get('scenario', {}).get(prop['scenario']['scenario'], {}),
                prop['app'], prop['scenario'], prop['attribute'])

        self.__check_nested_dir()

    def __update_category(self, prop_container, prop_app, prop_scenario, prop_attribute):
        if 'category' not in prop_container:
            return

        for ctg, ctg_prop in prop_container['category'].items():
            if ctg in self:
                _logger.warning('Conflicting category: %s', ctg)
            self.__load_category(ctg, ctg_prop, prop_app, prop_scenario, prop_attribute)

    def __load_category(self, ctg, ctg_prop, prop_app, prop_scenario, prop_attribute):
        self[ctg] = {}
        result = self[ctg]

        result['name'] = ctg
        result['pre_check'] = ctg_prop.get('pre_check', False)
        result['install'] = ctg_prop.get('install', False)
        result['auto_env'] = ctg_prop.get('auto_env', False)
        result['version_dir'] = ctg_prop.get('version_dir', False)
        result['shared'] = ctg_prop.get('shared', False)

        if 'root' not in ctg_prop:
            result['install'] = False
            result['auto_env'] = False
            result['shared'] = False
            return

        format_dict = {}
        format_dict.update(prop_attribute)
        format_dict.update(prop_scenario)
        result['root'] = expand_path(ctg_prop['root'].format(**format_dict))

        result['ctrl_dir'] = os.path.join(result['root'], prop_app['category_ctrl_dir'])
        if result['shared']:
            result['ctrl_package_dir'] = os.path.join(result['ctrl_dir'], 'shared')
        else:
            result['ctrl_package_dir'] = os.path.join(
                result['ctrl_dir'], 'release', prop_scenario['version'])
        result['ctrl_install_dir'] = os.path.join(result['ctrl_dir'], 'install')

    def __check_nested_dir(self):
        for ctg1, value1 in self.items():
            if 'root' not in value1:
                continue
            for ctg2, value2 in self.items():
                if ctg1 == ctg2:
                    continue
                if 'root' not in value2:
                    continue
                if value1['root'].startswith(value2['root']):
                    raise PropCategoryError(
                        'Nested category "{0}" - "{1}": "{2}" - "{3}"'
                        .format(ctg1, ctg2, value1['root'], value2['root']))
