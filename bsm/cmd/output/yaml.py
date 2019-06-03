import yaml
from bsm.util.config import dump_config_str

class Yaml(object):
    def dump(self, value):
        return dump_config_str(value)
