import copy

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from bsm.util.config import dump_config

from bsm.config.util import config_from_file


class CommonDict(MutableMapping):
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
        self.__data = config_from_file(config_file, dict)

    def update_from_file(self, config_file):
        self.__data.update(config_from_file(config_file, dict))

    def save_to_file(self, config_file):
        dump_config(self.__data, config_file)
