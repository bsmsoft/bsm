import yaml

from cepcenv.error import CepcenvError


class ConfigError(CepcenvError):
    pass


def load_config(fn):
    try:
        with open(fn, 'r') as f:
            return yaml.load(f)
    except Exception as e:
        raise ConfigError('Load config "%s" error (%s)' % (fn, e))

def dump_config(self, data, fn):
    try:
        with open(fn, 'w') as f:
            yaml.dump(data, f)
    except Exception as e:
        raise ConfigError('Write config "%s" error (%s)' % (fn, e))
