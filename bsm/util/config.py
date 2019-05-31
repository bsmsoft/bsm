import yaml


class ConfigError(Exception):
    pass


class ExplicitDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def load_config(fn):
    try:
        with open(fn, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ConfigError('Load config error: {0}'.format(e))

def dump_config(data, fn):
    try:
        with open(fn, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, Dumper=ExplicitDumper)
    except Exception as e:
        raise ConfigError('Dump config error: {0}'.format(e))

def load_config_str(config_str):
    try:
        return yaml.safe_load(config_str)
    except Exception as e:
        raise ConfigError('Load config from string error: {0}'.format(e))

def dump_config_str(data):
    try:
        return yaml.dump(data, default_flow_style=False, Dumper=ExplicitDumper)
    except Exception as e:
        raise ConfigError('Dump config error: {0}'.format(e))
