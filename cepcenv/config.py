import yaml

from cepcenv.error import CepcenvError


class ConfigError(CepcenvError):
    pass


def load_config(fn):
    try:
        with open(fn, 'r') as f:
            return yaml.load(f)
    except Exception as e:
        raise ConfigError('Load config "{0}" error ({1})'.format(fn, e))

def dump_config(data, fn):
    try:
        with open(fn, 'w') as f:
            yaml.dump(data, f)
    except Exception as e:
        raise ConfigError('Dump config "{0}" error ({1})'.format(fn, e))

def load_config_str(config_str):
    try:
        return yaml.load(config_str)
    except Exception as e:
        raise ConfigError('Load config from string error ({0})'.format(e))

def dump_config_str(data):
    try:
        return yaml.dump(data)
    except Exception as e:
        raise ConfigError('Dump config error ({0})'.format(e))
