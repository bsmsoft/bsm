import yaml

from bsm.error import ConfigLoadError
from bsm.error import ConfigDumpError


class ExplicitDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def load_config(filename):
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as e:
        raise ConfigLoadError('Load config error: {0}'.format(e))


def dump_config(data, filename):
    try:
        with open(filename, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, Dumper=ExplicitDumper)
    except (IOError, yaml.YAMLError) as e:
        raise ConfigDumpError('Dump config error: {0}'.format(e))


def load_config_str(config_str):
    try:
        return yaml.safe_load(config_str)
    except yaml.YAMLError as e:
        raise ConfigLoadError('Load config from string error: {0}'.format(e))


def dump_config_str(data):
    try:
        return yaml.dump(data, default_flow_style=False, Dumper=ExplicitDumper)
    except yaml.YAMLError as e:
        raise ConfigDumpError('Dump config error: {0}'.format(e))
