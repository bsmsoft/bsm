import collections
import copy

from bsm.config import ConfigNoDirectModError

from bsm.util.config import load_config
from bsm.util.config import dump_config
from bsm.util.config import ConfigError

from bsm.logger import get_logger
_logger = get_logger()


class Common(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__data = dict()
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


    @property
    def data(self):
        return self.__data

    @property
    def data_copy(self):
        return copy.deepcopy(self.__data)


    def load_from_file(self, config_file):
        self.__data = dict()
        try:
            loaded_data = load_config(config_file)
            if isinstance(loaded_data, dict):
                self.__data = loaded_data
            else:
                _logger.warn('Config file is not a dict: {0}'.format(config_file))
                _logger.warn('Use empty dict instead')
        except ConfigError as e:
            _logger.debug('Load config file "{0}" failed: {1}'.format(config_file, e))
            _logger.debug('Use empty dict instead')

    def save_to_file(self, config_file):
        dump_config(self.__data, config_file)
