import os
import random
import string
import datetime

from bsm.config.common import Common

from bsm.util import expand_path
from bsm.util import ensure_list

from bsm import HANDLER_MODULE_NAME


_SCENARIO_GLOBAL_ITEMS = ('software_root', 'release_repo')
_SCENARIO_ENTRY_ITEMS = ('software_root', 'release_repo', 'release_source')
_SCENARIO_PATH_ITEMS = ('software_root', 'release_source')


__TEMP_VERSION_PREFIX = ''
__TEMP_VERSION_LENGTH = 6

def _temp_version():
    return __TEMP_VERSION_PREFIX \
            + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f') + '_' \
            + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(__TEMP_VERSION_LENGTH))

def _filter_scenario_config(config, items, veto=False):
    ''' If veto is False, config only in items will be included
        If veto is True, all config except in items will be included
    '''
    scenario_config = {}

    for k, v in config.items():
        if v is None:
            continue

        # This is equivalent to xor operation
        if (k in items) != veto:
            scenario_config[k] = v

    return scenario_config


class ConfigScenarioError(Exception):
    pass


class Scenario(Common):
    def __init__(self):
        super(Scenario, self).__init__()

        self.__version_path = {}

    def load_scenario(self, config_entry, config_user, config_app):
        self['option'] = {}

        self.update(_filter_scenario_config(config_app, _SCENARIO_GLOBAL_ITEMS))

        self.update(_filter_scenario_config(config_user, _SCENARIO_GLOBAL_ITEMS))
        self.__update_option(config_user)

        if 'scenario' in config_entry:
            scenario = config_entry['scenario']
            self['scenario'] = scenario

            if 'scenario' in config_user and scenario in config_user['scenario']:
                self.update(_filter_scenario_config(config_user['scenario'][scenario], ['option'], True))
                self.__update_option(config_user['scenario'][scenario])

            if 'version' not in self:
                self['version'] = scenario

        self.update(_filter_scenario_config(config_entry, _SCENARIO_ENTRY_ITEMS))
        self.__update_option(config_entry)

        if 'version' not in self:
            self['version'] = _temp_version()

        self.__expand_path()
        self.__load_version_path(config_app)


    def __update_option(self, config_container):
        if 'option' not in config_container:
            return

        config_option = config_container['option']
        if isinstance(config_option, dict):
            self['option'].update(config_option)

    def __expand_path(self):
        for k in _SCENARIO_PATH_ITEMS:
            if k in self:
                self[k] = expand_path(self[k])

    def __load_version_path(self, config_app):
        self.__version_path = {}

        if 'software_root' not in self:
            raise ConfigScenarioError('"software_root" not specified in configuration')

        self.__version_path['release_dir'] = os.path.join(self['software_root'], config_app['release_dir'])
        self.__version_path['main_dir'] = os.path.join(self.__version_path['release_dir'], self['version'])
        self.__version_path['def_dir'] = os.path.join(self.__version_path['main_dir'], 'def')
        self.__version_path['config_dir'] = os.path.join(self.__version_path['def_dir'], 'config')
        self.__version_path['handler_dir'] = os.path.join(self.__version_path['def_dir'], 'handler')
        self.__version_path['handler_python_dir'] = os.path.join(self.__version_path['main_dir'], 'handler')
        self.__version_path['handler_module_dir'] = os.path.join(self.__version_path['main_dir'], 'handler', HANDLER_MODULE_NAME)
        self.__version_path['status_dir'] = os.path.join(self.__version_path['main_dir'], 'status')
        self.__version_path['install_status_file'] = os.path.join(self.__version_path['status_dir'], 'install.yml')


    @property
    def version_path(self):
        return self.__version_path
