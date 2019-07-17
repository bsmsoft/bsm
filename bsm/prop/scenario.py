from bsm.util import expand_path

from bsm.prop.common_dict import CommonDict


_SCENARIO_GLOBAL_ITEMS = ('software_root', 'release_repo')
_SCENARIO_ENTRY_ITEMS = ('software_root', 'release_repo', 'release_source', 'version')
_SCENARIO_SCENARIO_ITEMS = ('software_root', 'release_repo', 'release_source', 'version')
_SCENARIO_PATH_ITEMS = ('software_root', 'release_source')


def _filter_scenario_prop(prop, items, veto=False):
    ''' If veto is False, prop only in items will be included
        If veto is True, all prop except in items will be included
    '''
    scenario_prop = {}

    for k, v in prop.items():
        if v is None:
            continue

        # This is equivalent to xor operation
        if (k in items) != veto:
            scenario_prop[k] = v

    return scenario_prop


class Scenario(CommonDict):
    def __init__(self, prop):
        super(Scenario, self).__init__()

        self.update(_filter_scenario_prop(prop['app'], _SCENARIO_GLOBAL_ITEMS))

        self.update(_filter_scenario_prop(prop['user'], _SCENARIO_GLOBAL_ITEMS))

        use_default = bool(prop['entry'].get('default_scenario') and
                           prop['info'].get('default', {}).get('scenario'))

        scenario = None
        if 'scenario' in prop['entry'] and prop['entry']['scenario']:
            scenario = prop['entry']['scenario']
        elif use_default:
            scenario = prop['info']['default']['scenario']
        elif 'scenario' in prop['env'] and prop['env']['scenario']:
            scenario = prop['env']['scenario']

        if scenario:
            self['scenario'] = scenario

            self.update(_filter_scenario_prop(prop['user'].get('scenario', {}).get(scenario, {}),
                                              _SCENARIO_SCENARIO_ITEMS))

            if 'version' not in self:
                self['version'] = scenario


        if use_default:
            if prop['info'].get('default', {}).get('software_root'):
                self['software_root'] = prop['info']['default']['software_root']
        else:
            if prop['env'].get('software_root'):
                self['software_root'] = prop['env']['software_root']

        self.update(_filter_scenario_prop(prop['entry'], _SCENARIO_ENTRY_ITEMS))

        self.__expand_path()

    def __expand_path(self):
        for k in _SCENARIO_PATH_ITEMS:
            if k in self:
                self[k] = expand_path(self[k])
