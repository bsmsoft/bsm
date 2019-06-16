import collections
import copy

from bsm.util.config import load_config, dump_config, ConfigError

from bsm.logger import get_logger
_logger = get_logger()


def _config_from_file(config_file):
    try:
        loaded_data = load_config(config_file)
        if isinstance(loaded_data, dict):
            return loaded_data
        _logger.warn('Config file is not a dict, use empty dict instead: {0}'.format(config_file))
    except ConfigError as e:
        _logger.debug('Load config file failed, use empty dict instead: {0}'.format(config_file))
    return {}


class Common(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__data = {}
        self.update(dict(*args, **kwargs))


    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __delitem__(self, key):
        del self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __repr__(self):
        return repr(self.__data)


    def data(self):
        return self.__data

    def data_copy(self):
        return copy.deepcopy(self.__data)


    def load_from_file(self, config_file):
        self.__data = _config_from_file(config_file)

    def update_from_file(self, config_file):
        self.__data.update(_config_from_file(config_file))

    def save_to_file(self, config_file):
        dump_config(self.__data, config_file)
