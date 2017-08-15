from cepcenv.util import is_str

class Scenario(object):
    def __init__(self, config):
        self.__config = config

    def __default_scenario_config(self):
        scenario_config = {}

        if 'release_root' in self.__config:
            scenario_config['release_root'] = self.__config['release_root']

        if 'workarea' in self.__config:
            scenario_config['workarea'] = self.__config['workarea']

        return scenario_config

    def load(self, scenario_name):
        scenario_config = self.__default_scenario_config()

        if is_str(scenario_name):
            if 'scenario' in self.__config and scenario_name in self.__config['scenario']:
                scenario_config.update(self.__config['scenario'])
            else:
                scenario_config['release_version'] = scenario_name

        return scenario_config
