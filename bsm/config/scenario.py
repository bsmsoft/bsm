from bsm.util import expand_path

from bsm.config.common_dict import CommonDict


_SCENARIO_GLOBAL_ITEMS = ('software_root', 'release_repo')
_SCENARIO_ENTRY_ITEMS = ('software_root', 'release_repo', 'release_source', 'version')
_SCENARIO_SCENARIO_ITEMS = ('software_root', 'release_repo', 'release_source', 'version')
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


class Scenario(CommonDict):
    def __init__(self, config):
        super(Scenario, self).__init__()

        self.update(_filter_scenario_config(config['app'], _SCENARIO_GLOBAL_ITEMS))

        self.update(_filter_scenario_config(config['user'], _SCENARIO_GLOBAL_ITEMS))

        use_default = bool(config['entry'].get('default_scenario') and config['info'].get('default', {}).get('scenario'))

        scenario = None
        if 'scenario' in config['entry'] and config['entry']['scenario']:
            scenario = config['entry']['scenario']
        elif use_default:
            scenario = config['info']['default']['scenario']
        elif 'scenario' in config['env'] and config['env']['scenario']:
            scenario = config['env']['scenario']

        if scenario:
            self['scenario'] = scenario

            self.update(_filter_scenario_config(config['user'].get('scenario', {}).get(scenario, {}), _SCENARIO_SCENARIO_ITEMS))

            if 'version' not in self:
                self['version'] = scenario


        if use_default:
            if config['info'].get('default', {}).get('software_root'):
                self['software_root'] = config['info']['default']['software_root']
        else:
            if config['env'].get('software_root'):
                self['software_root'] = config['env']['software_root']

        self.update(_filter_scenario_config(config['entry'], _SCENARIO_ENTRY_ITEMS))

        self.__expand_path()

    def __expand_path(self):
        for k in _SCENARIO_PATH_ITEMS:
            if k in self:
                self[k] = expand_path(self[k])
