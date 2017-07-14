class Scenario(object):
    def __init__(self, config):
        self.__config = config

    def load(self, scenario_name):
        scenario = {}
        if 'scenario' in self.__config and scenario_name in self.__config['scenario']:
            scenario.update(self.__config['scenario'])
        else:
            scenario['release_version'] = scenario_name

        if 'cepcsoft_root' not in scenario:
            scenario['cepcsoft_root'] = self.__config['cepcsoft_root']

        if 'workarea' not in scenario and 'workarea' in self.__config:
            scenario['workarea'] = self.__config['workarea']
