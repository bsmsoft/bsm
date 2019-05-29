import os
import random
import string
import datetime

from bsm.config.common import Common

from bsm.util import expand_path
from bsm.util import ensure_list


_SCENARIO_GLOBAL_ITEMS = ('software_root', 'release_repo')
_SCENARIO_ENTRY_ITEMS = ('software_root', 'release_repo', 'release_source')
_SCENARIO_PATH_ITEMS = ('software_root', 'release_source')


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
    def load(self, config_entry, config_app, config_env, config_user):
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

        self.__expand_path()


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
