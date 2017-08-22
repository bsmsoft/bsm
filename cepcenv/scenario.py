from cepcenv.util import is_str
from cepcenv.software_platform import SoftwarePlatform

__scenario_items = ('release_root', 'release_version', 'release_config', 'workarea', 'platform', 'os', 'arch', 'compiler')

def __filter_scenario_config(config):
    scenario_config = {}

    for k, v in config.items():
        if k in __scenario_items and v is not None:
            scenario_config[k] = v

    return scenario_config

def __scenario_config_specific(config, scenario_name):
    scenario_config = {}

    if is_str(scenario_name):
        if 'scenario' in config and scenario_name in config['scenario']:
            scenario_config = __filter_scenario_config(config['scenario'][scenario_name])
        else:
            scenario_config['release_version'] = scenario_name

    return scenario_config


def load_scenario(config, scenario_name=None, scenario_config_cmd={}):
    scenario_config = __filter_scenario_config(config)
    scenario_config.update(__scenario_config_specific(config, scenario_name))
    scenario_config.update(__filter_scenario_config(scenario_config_cmd))

    sp = SoftwarePlatform(scenario_config.get('arch'), scenario_config.get('os'), scenario_config.get('compiler'))
    if 'arch' not in scenario_config or not scenario_config['arch']:
        scenario_config['arch'] = sp.arch
    if 'os' not in scenario_config or not scenario_config['os']:
        scenario_config['os'] = sp.os
    if 'compiler' not in scenario_config or not scenario_config['compiler']:
        scenario_config['compiler'] = sp.compiler
    if 'platform' not in scenario_config or not scenario_config['platform']:
        scenario_config['platform'] = sp.platform

    return scenario_config
